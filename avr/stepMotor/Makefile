MCU=atmega16
CC=avr-gcc
OBJCOPY=avr-objcopy
CFLAGS=-mmcu=$(MCU) -Wall

# settings for avrude 
PROGRAMMER=avrdude
BOARD=stk500
PORT=/dev/ttyUSB0
PFLAGS=-p $(MCU) -c $(BOARD) -P $(PORT)

stepMotor.out : stepMotor.o
	$(CC) $(CFLAGS) -o stepMotor.out -Wl,-Map,stepMotor.map stepMotor.o

stepMotor.o : stepMotor.c
	$(CC) $(CFLAGS) -Os -c stepMotor.c

clean:
	rm -f *.o *.out *.map *.hex *.i *.s

program:
	$(PROGRAMMER) $(PFLAGS) -e
	#$(PROGRAMMER) $(PFLAGS) -U stepMotor.out
