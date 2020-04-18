MCU = atmega16
CC=avr-gcc
OBJCOPY=avr-objcopy
CFLAGS= -mmcu=$(MCU) -Wall 

# settings for avrude 
PROGRAMMER = avrdude
BOARD = stk500
#PORT = /dev/ttyUSB0
PORT = /dev/ttyS0
PFLAGS = -p $(MCU) -c $(BOARD) -P $(PORT)

first.out: first.o lcd.o
	$(CC) $(CFLAGS) -o first.out -Wl,-Map,first.map first.o lcd.o

first.o: first.c
	$(CC) $(CFLAGS) -Os -c first.c

lcd.o: lcd.c
	$(CC) $(CFLAGS) -Os -c lcd.c

clean:
	rm -f *.o *.out *.map *.hex *.i *.s

program:
	$(PROGRAMMER) $(PFLAGS) -U first.out
