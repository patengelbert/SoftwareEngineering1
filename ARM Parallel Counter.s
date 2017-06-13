	AREA ArmExample, CODE

ENTRY
		MOV r0, #0xAB000000
		MOV r1, #0xF000000F
		MOV r2, #0xFC000000
		EOR r4, r0, r1
		AND r6, r0, r1
		ADD r5, r5, r6
		AND r6, r4, r2
		EOR r4, r4, r2
		ADD r5, r5, r6

STOP    B STOP
