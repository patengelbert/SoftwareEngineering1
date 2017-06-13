	AREA	ArmExample,	CODE
ENTRY
		MOV r1, #&8
		MOV r2, #&9
		CMP r2, r1
		BMI SWAP
		B	STOP

SWAP	MOV r3, r1
		MOV r1, r2
		MOV r2, r3
		B	STOP

STOP	B	STOP

	    END