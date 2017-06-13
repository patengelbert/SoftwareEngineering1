	AREA ARMSubrx, CODE, READWRITE
		ENTRY
		
		LDR r13, =STACKL + 36

		MOV r1, #5
		MOV r2, #3

		BL MULT

		ADD r3, r0, #1

STOP	B STOP

MULT	STMED r13!, {r1, r14}
		MOV r0, #0
		CMP r1, #0
		BEQ MULTEND

MULOOP	ADD r0, r0, r2
		SUBS r1, r1, #1
		BNE MULOOP

MULTEND	LDMED r13!, {r1, pc}

STACKL 	FILL 40

		END