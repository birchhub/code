#define F_CPU 1000000UL /* Clock Frequency = 1Mhz */

#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>

void T0delay();
void delay_second();

long seconds=0;
char secCnt=0;

// timer0 overflow interrupt
ISR(TIMER0_OVF_vect)
{
	if (++secCnt == 4) {
		secCnt = 0;
		PORTB = ~PORTB;
		seconds++;
	}
	TCNT0 = 0x12;
}

int main() {

	DDRB = 0xFF; // Set all the pins of PORTB as output

	unsigned char value = 0xF0; // LSB = PORTx0, 1 -> LED ist aus
	PORTB = value;

	// via interrupt
	// enable timer interrupts for timer0
	TIMSK = 0x01;
	// start value of timer. then starts from this value up to 255
	TCNT0 = 0x12;
	// clock-source + prescaling
	TCCR0 = 0x5;

	// enable interrupts
	sei();
	while(1);

	
	// non-interrupt way
//	while (1) {
//		value = ~value;
//		PORTB = value;
//		//_delay_ms(200);
//		delay_second();
//	}

}

void delay_second()
{
	for (int i=0; i<4; i++) {
		T0delay();
	}
}

void T0delay()
{
	// start value of timer. then starts from this value up to 255
	TCNT0 = 0x12;
	
	// clock-source + prescaling
	TCCR0 = 0x5;

	// TIFR.. 	global register for all timers
	// LSB=1..	we had an overflow
	while ((TIFR & 0x01) == 0);
	
	// disable timer
	TCCR0 = 0;

	// clear flag by writing 1 into it
	TIFR |= 0x01;
}
