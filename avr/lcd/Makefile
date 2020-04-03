MCU = atmega16
CC=avr-gcc
OBJCOPY=avr-objcopy
CFLAGS= -mmcu=$(MCU) -Wall 

# settings for avrude 
PROGRAMMER = avrdude
BOARD = stk500
PORT = /dev/ttyUSB0
PFLAGS = -p $(MCU) -c $(BOARD) -P $(PORT)

lcd.out : lcd.o
	$(CC) $(CFLAGS) -o lcd.out -Wl,-Map,lcd.map lcd.o

lcd.o : lcd.c
	$(CC) $(CFLAGS) -Os -c lcd.c

clean:
	rm -f *.o *.out *.map *.hex *.i *.s

program:
	$(PROGRAMMER) $(PFLAGS) -U lcd.out
