; Standard definitions of Mode bits and Interrupt (I & F) flags in PSRs

Mode_USR        EQU     0x10
Mode_FIQ        EQU     0x11
Mode_IRQ        EQU     0x12
Mode_SVC        EQU     0x13
Mode_ABT        EQU     0x17
Mode_UND        EQU     0x1B
Mode_SYS        EQU     0x1F

I_Bit           EQU     0x80            ; when I bit is set, IRQ is disabled
F_Bit           EQU     0x40            ; when F bit is set, FIQ is disabled


;// <h> Stack Configuration (Stack Sizes in Bytes)
;//   <o0> Undefined Mode      <0x0-0xFFFFFFFF:8>
;//   <o1> Supervisor Mode     <0x0-0xFFFFFFFF:8>
;//   <o2> Abort Mode          <0x0-0xFFFFFFFF:8>
;//   <o3> Fast Interrupt Mode <0x0-0xFFFFFFFF:8>
;//   <o4> Interrupt Mode      <0x0-0xFFFFFFFF:8>
;//   <o5> User/System Mode    <0x0-0xFFFFFFFF:8>
;// </h>

UND_Stack_Size  EQU     0x00000000
SVC_Stack_Size  EQU     0x00000080
ABT_Stack_Size  EQU     0x00000000
FIQ_Stack_Size  EQU     0x00000000
IRQ_Stack_Size  EQU     0x00000080
USR_Stack_Size  EQU     0x00000000

ISR_Stack_Size  EQU     (UND_Stack_Size + SVC_Stack_Size + ABT_Stack_Size + \
                         FIQ_Stack_Size + IRQ_Stack_Size)

        		AREA     RESET, CODE
				ENTRY
;  Dummy Handlers are implemented as infinite loops which can be modified.

Vectors         LDR     PC, Reset_Addr         
                LDR     PC, Undef_Addr
                LDR     PC, SWI_Addr
                LDR     PC, PAbt_Addr
                LDR     PC, DAbt_Addr
                NOP                            ; Reserved Vector 
                LDR     PC, IRQ_Addr
;               LDR     PC, [PC, #-0x0FF0]     ; Vector from VicVectAddr
                LDR     PC, FIQ_Addr

ACBASE			DCD		P0COUNT
SCONTR			DCD		SIMCONTROL

Reset_Addr      DCD     Reset_Handler
Undef_Addr      DCD     Undef_Handler
SWI_Addr        DCD     SWI_Handler
PAbt_Addr       DCD     PAbt_Handler
DAbt_Addr       DCD     DAbt_Handler
                DCD     0                      ; Reserved Address 
FIQ_Addr        DCD     FIQ_Handler

Undef_Handler   B       Undef_Handler
SWI_Handler     B       SWI_Handler
PAbt_Handler    B       PAbt_Handler
DAbt_Handler    B       DAbt_Handler
FIQ_Handler     B       FIQ_Handler


				AREA 	ARMuser, CODE,READONLY

IRQ_Addr        DCD     ISR_FUNC1
EINT2			EQU 	16
Addr_VicIntEn	DCD		0xFFFFF010	 	; set to (1<<EINT0)
Addr_EXTMODE	DCD 	0xE01FC148   	; set to 1
Addr_PINSEL0	DCD		0xE002C000		; set to 2_1100
Addr_EXTINT		DCD		0xE01FC140

;  addresses of two registers that allow faster input

Addr_IOPIN		DCD		0xE0028000


; Initialise the Interrupt System
;  ...
ISR_FUNC1		STMED	R13!, {R0,R1}
				MOV 	R0, #(1 << 2) 	   ; bit 2 of EXTINT
				LDR 	R1,	Addr_EXTINT	   
				STR		R0, [R1]		   ; EINT2 reset interrupt
				LDMED	R13!, {R0,R1}
				B 		ISR_FUNC

Reset_Handler
; PORT0.1 1->0 triggers EINT0 IRQ interrupt
				MOV R0, #(1 << EINT2)
				LDR R1, Addr_VicIntEn
				STR R0, [R1]
				MOV R0, #(1 << 30)
				LDR R1, Addr_PINSEL0
				STR R0, [R1]
				MOV R0, #(1 << 2)
				LDR R1, Addr_EXTMODE
				STR R0, [R1]

;  Setup Stack for each mode

                LDR     R0, =Stack_Top

;  Enter Undefined Instruction Mode and set its Stack Pointer
                MSR     CPSR_c, #Mode_UND:OR:I_Bit:OR:F_Bit
                MOV     SP, R0
                SUB     R0, R0, #UND_Stack_Size

;  Enter Abort Mode and set its Stack Pointer
                MSR     CPSR_c, #Mode_ABT:OR:I_Bit:OR:F_Bit
                MOV     SP, R0
                SUB     R0, R0, #ABT_Stack_Size

;  Enter FIQ Mode and set its Stack Pointer
                MSR     CPSR_c, #Mode_FIQ:OR:I_Bit:OR:F_Bit
                MOV     SP, R0
                SUB     R0, R0, #FIQ_Stack_Size

;  Enter IRQ Mode and set its Stack Pointer
                MSR     CPSR_c, #Mode_IRQ:OR:I_Bit:OR:F_Bit
                MOV     SP, R0
                SUB     R0, R0, #IRQ_Stack_Size

;  Enter Supervisor Mode and set its Stack Pointer
                MSR     CPSR_c, #Mode_SVC:OR:F_Bit
                MOV     SP, R0
                SUB     R0, R0, #SVC_Stack_Size
				B 		START
;----------------------------DO NOT CHANGE ABOVE THIS COMMENT--------------------------------
;--------------------------------------------------------------------------------------------
;--------------------------------------------------------------------------------------------


;****************************************************************************************** 
; Author: Patrick Engelbert 
; Purpose: Count the changes from 0 to 1 for 4 different frequencies up to maximum of 200 000 repetitions
; Date: January 2014
; Code overview: 
;					My code works by using a BIC intruction to detect changes from a 0 to a 1 in the input pins.
;					The code counts all 4 values in parallel using 8 bits and uses the 8th bit of each count as a form of carry flag
;					When the count reaches 0b10000000, the overflow intructions are executed to stop errors
;					The code uses 3 registers (18 bits) to be able to fit the value 200 000 which is the maximum required
;****************************************************************************************** 



SCS_REGISTER	DCD		0xE01FC1A0							   ;Status Memory address
FIOMASK			DCD		0x3FFFC010							   ;FP0xMASK Memory address
FIOPIN			DCD		0x3FFFC014							   ;FIO0PIN Memory address

;****************************************************************************************** 
;This uses information from page 47 of the UM10161 User Manual
;****************************************************************************************** 

START		   	MOV		R1,  #0x00000001
				LDR 	R11, =0xFEFEFEFE			  ;As FIOMASK is active low, this will cause the inputs to only show input bits 0, 8, 16, 24
				LDR		R10, SCS_REGISTER			  ;Set Status register to use GPIO input rather than standard IO register
				LDR		R0, [R10]					  ;This will allow me to use a bit mask instruction while loading, removing the bit mask in the loop
				ORR		R0,  R0, R1					  ;I do not know what is in the Status register so I only wish to change bit 0 to 1
				STR		R0, [r10]
				LDR		R10, FIOMASK				  ;Set FIOMASK with the required mask
				MOV		R0,  R11
				STR		R0, [r10]



				LDR		R1, =0x11111111 ;Set to this value so when the bic command I operted on it, the output will be 0x00000000
				MOV		R4, #0x00000000	;count, bits 0-6
				MOV		R5, #0x00000000	;count, bit 7-14
				LDR		R7, =0x01010101	;The starting states of all of the inputs, they all start high
				MOV		R8, #0x00000000	;count, bit 15-23
				LDR 	R9,	=0x01010101	;a bit mask to get only the input bits as the rest could be any value
				LDR		R10, FIOPIN	;The address of the input memory location, which uses the GPIO Input rather than the standard input
				LDR 	R11, =0x7F7F7F7F ;A bit mask to get rid of the overflow bit

				


				;Registers R0, R2, R3, R6, R12 are used in the code for the following operations:
				; R0 - No use until the storing of information
				; R2 - Used to load every second input in conjction with R1
				; R3 - Temporary register to store numbers to be added to the count
				; R6 - Multiple uses as a temporary register
				; R12 - Used to load the input once per loop 

								
LOOP	    	LDR	R12, [R10]	 
				BIC	R3, R12, R7	 
				ADD	R4, R4, R3	 

				;This loop is special as it includes an instruction to allow counting 
				;through through the branch at the end of the code
				;as such the proper code segment that has been unrolled starts at the next copy 

				;The basic algorithm used is:
				LDR	R2, [R10]	 	;Load the data
				BIC	R3, R2, R12	 	;Bit clear with the previous values of the input. Thus R3 will only be 1 if the current value is 1 and the previou value 0
				ADD	R4, R4, R3	 	;Add the number of changes to the count register, as the value will either be 1 (change), or 0 (no change)

				

				BIC	R6, R7, R1	 ;This line is the third instruction of the count segment, however it references to a load from before the branch instruction
				

				LDR	R1, [R10]	 ;this is another copy of my algorithm, however it use a different register	to store the value
				BIC	R3, R1, R2	 ;make the current value into the old value
				ADD	R4, R4, R3	 

				ADD	R4, R4, R6	 ;This line is the final instruction of the count segment, however it references to a load from before the branch instruction


				LDR	R2, [R10]	  
				BIC	R3, R2, R1	 
				ADD	R4, R4, R3	 

				AND  R6, R4, R9, lsl #7	;This is the first part of my overflow intruction, these intructions are interpersed between my basic algorithm. 
				;combined my overflow check looks like this:
				;AND  R6, R4, R9, lsl #7	 This is a bit mask to check if the 8th bit of each count is 1. It uses a mask of 0x80808080 which is created by a shift of 0x01010101
				;AND  R4, R4, R11			 This clears this 'carry' bit to stop any actual overflow between counts occuring
				;ADD  R5, R5, R6, lsr #7	 This adds the overflow to the overflow count, similar to the changes being added to the original count
				
				LDR	R1, [R10]	 
				AND	R4, R4, R11	 ;This is the second part of my overflow intruction
				BIC	R3, R1, R2	 
				ADD	R4, R4, R3	 
										  
				LDR	R2, [R10]	 	 
				BIC	R3, R2, R1	 
				ADD	R4, R4, R3	 

				ADD	R5, R5, R6, lsr #7 ;This is the last part of my overflow intruction

				LDR	R1, [R10]	 
				BIC	R3, R1, R2	 
				ADD	R4, R4, R3	 

				AND  R6, R5, R9, lsl #7	;As the count can go up to 20 000 000, the overflow may be too small and so that may overflow too
								    	;Thus I use three registers for counting and have to check for overflow on the second register 
										;This is done in the same way as the original overflow, using different registers
				LDR	R2, [R10]	 
				AND	R5, R5, R11	  ;This is the second part of my overflow's overflow instruction
				BIC	R3, R2, R1	 
				ADD	R4, R4, R3	 			

				LDR	R1, [R10]	 	 
				BIC	R3, R1, R2	 
				ADD	R4, R4, R3	 
				
				ADD	R8, R8, R6, lsr #7 ;This is the last part of my overflow's overflow instruction

				LDR	R2, [R10]	 
				CMP		R9, #0x0000000	 ;Here I check if the IRQ function has changed a variable, I chose to use the bit mask in case the interrupt occurs early on as I do not want to read the input at that point 		 
				BIC	R3, R2, R1	 
				ADD	R4, R4, R3	 
	

				LDR	R1, [R10]	 
				BIC	R3, R1, R2	 
				ADD	R4, R4, R3	 

	  			LDR	R7, [R10]	 ;This is my pre-branch load, the actual processing instructions are located earlier in the loop. 
								 ;I have done this so that the maximum delay between the ends two consecutive LDR commands is 7
								 ;As the sampling rate has to be twice the frequency, the time period of sampling (in my case loading) must be double the time period of the input
								 ;Thus my lowest time period that I can read is 12

				BNE		LOOP	 					;Loop End. If the earlier compare intruction was false (and so Z=0) it will loop back to the beginning

				AND  R6, R4, R9, lsl #7	;one last check for overflow
				AND	R4, R4, R11	   		;in case IRQ occured between the last overflow check and the compare instruction
				ADD	R5, R5, R6, lsr #7 

				AND  R6, R5, R9, lsl #7	
				AND	R5, R5, R11	   
				ADD	R8, R8, R6, lsr #7 

				
				LDR		R0, =P0COUNT          ;This segment, sorts the pieces of the three count register into a single number for P0Count
				AND		R6, R4, #0x0000007F	  ;This is done by selecting only the relevant bits, shifting them into the correct place 
				AND 	R7, R5, #0x0000007F	  ;These pieces are added onto register R9 and stores this value in the memory location
				AND 	R1, R8, #0x000000FF	  ;I don't check bit 8 as it is my 'carry bit' and is going to be 0 in all cases 
				MOV		R9, R6
				ADD		R9, R9, R7, lsl #7
				ADD		R9, R9, R1, lsl #14
				STR		R9, [R0]
				
				LDR		R0, =P1COUNT			;This segment is a repeat of the previous, only using a different amount of shifts and
				AND		R6, R4, #0x00007F00		;Selecting a different part of the counts
				AND 	R7, R5, #0x00007F00		;Repeat for P2 
				AND 	R1, R8, #0x0000FF00
				MOV		R9, R6, lsr #8
				ADD		R9, R9, R7, lsr #1
				ADD		R9, R9, R1, lsl #6
				STR		R9, [R0]
				
				LDR		R0, =P2COUNT			;Repeat for P2 
				AND		R6, R4, #0x007F0000
				AND 	R7, R5, #0x007F0000
				AND 	R1, R8, #0x00FF0000
				MOV		R9, R6, lsr #16
				ADD		R9, R9, R7, lsr #9
				ADD		R9, R9, R1, lsr #2
				STR		R9, [R0]
				
				LDR		R0, =P3COUNT			;Repeat for P3 
				AND		R6, R4, #0x7F000000
				AND 	R7, R5, #0x7F000000
				AND 	R1, R8, #0xFF000000
				MOV		R9, R6, lsr #24
				ADD		R9, R9, R7, lsr #17
				ADD		R9, R9, R1, lsr #10
				STR		R9, [R0]


				
	
				B		LOOP_END					;End of program	



ISR_FUNC		MOV		R9, #0x00000000		;I change the bit mask to 0. The reasoning behind this is outlined on line 231
			
				SUBS		pc, R14, #4		;exit IRQ mode and return to the place where the interrupt occured 		
										

;--------------------------------------------------------------------------------------------
; PARAMETERS TO CONTROL SIMULATION, VALUES MAY BE CHANGED TO IMPLEMENT DIFFERENT TESTS
;--------------------------------------------------------------------------------------------
SIMCONTROL
SIM_TIME 		DCD  	2576256	  ; length of simulation in cycles (100MHz clock)
P0_PERIOD		DCD   	86	  		; bit 0 input period in cycles
P1_PERIOD		DCD     60		  ; bit 8 input period in cycles
P2_PERIOD		DCD  	12		  ; bit 16 input period	in cycles
P3_PERIOD		DCD		26		  ; bit 24 input period	in cycles
;---------------------DO NOT CHANGE AFTER THIS COMMENT---------------------------------------
;--------------------------------------------------------------------------------------------
;-------------------------------------------------------------------------------   ------------
LOOP_END		MOV R0, #0x7f00
				LDR R0, [R0] 	; read memory location 7f00 to stop simulation
STOP			B 	STOP
;-----------------------------------------------------------------------------
 				AREA	DATA, READWRITE

P0COUNT			DCD		0
P1COUNT			DCD		0
P2COUNT			DCD		0
P3COUNT			DCD		0
;------------------------------------------------------------------------------			
                AREA    STACK, NOINIT, READWRITE, ALIGN=3

Stack_Mem       SPACE   USR_Stack_Size
__initial_sp    SPACE   ISR_Stack_Size

Stack_Top


        		END                     ; Mark end of file

