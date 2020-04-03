#define F_CPU 1000000UL /* Clock Frequency = 1Mhz */

#include <util/delay.h>
#include <avr/io.h>


int main() {

	DDRB = 0xFF; // Set all the pins of PORTB as output
	DDRD = 0x00; // Set all the pins of PortD as input

	unsigned char value = 0x00; // LSB = PORTx0
	//PORTB = value; 			//Turns off the output on the micro-controllers port C
	// auf 1 -> LED ist aus
	
	while (1) {
		value = PIND;
		//PORTB = value;
		if ((value & 0x01) != 1) {
			// switch0 pressed
			PORTB = 0x80;
		} else {
			PORTB = 0x0F;
		}
		_delay_ms(200);
	}

}
