#define F_CPU 1000000UL /* Clock Frequency = 1Mhz */

#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>

#include "lcd.h"

/*
 *	PORTD2 = INT0 wird fuer clock verwendet
 */

static char counter = 0;
static char tmpValue = 0;
static char recvValue = 0;
volatile static char newData = 0;
ISR(INT0_vect)
{
	if (PIND & 0x02) {
		// we got a 1
		tmpValue |= (1<<counter);
	}
	counter++;

	if (counter == 8) {
		// we received one byte
		counter=0;

		newData = 1;
		PORTB = ~tmpValue;
		recvValue = tmpValue;
		tmpValue = 0;
	}
}

int main() {

	DDRA = 0xFF; // Set all the pins of PORTB as output
	DDRB = 0xFF; // Set all the pins of PORTB as output
	PORTB = 0xff;
	DDRD = 0x00; // Set all the pins of PortD as input
	// D2.. clk
	// D1.. RX (is TX on the other side!)
	
	// enable external interrupt on port d2
	GICR |= 1<<INT0;
	MCUCR |= (1<<ISC00 | 1<<ISC01);
	sei();

	LCD_Init();
	LCD_Clear();
	LCD_Str("Uptime:");
	
	// auf 1 -> LED ist aus
	while (1) {
		if (newData) {
			newData=0;
			char val = recvValue;
			if (val >= 0x20 && val <= 0x7f) {
				LCD_Write(recvValue);
			} else if (val == 0x03) {
				LCD_Clear();
			}
		}
		_delay_ms(50);
	}

}
