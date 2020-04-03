MCU = atmega16
CC=avr-gcc
OBJCOPY=avr-objcopy
CFLAGS= -mmcu=$(MCU) -Wall 

# settings for avrude 
PROGRAMMER = avrdude
BOARD = stk500
PORT = /dev/ttyUSB0
PFLAGS = -p $(MCU) -c $(BOARD) -P $(PORT)

first.out : first.o
	$(CC) $(CFLAGS) -o first.out -Wl,-Map,first.map first.o

first.o : first.c
	$(CC) $(CFLAGS) -Os -c first.c

clean:
	rm -f *.o *.out *.map *.hex *.i *.s

program:
	$(PROGRAMMER) $(PFLAGS) -U first.out
