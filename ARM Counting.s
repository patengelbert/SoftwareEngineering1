	AREA		ArmExample,   CODE
	ENTRY
		MOV r1, #0
LOOP	ADD r1, r1, #1
		B LOOP
   END