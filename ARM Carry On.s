   AREA		 ArmExample, CODE

   ENTRY
	  MOV r0, #0xFFFFFFFF
	  MOV r1, #0xC
	  MOV r2, #0x1
	  MOV r3, #0x0
	  ADDS r4, r2, r0
	  ADCS r5, r3, r1

STOP  B STOP

	END

