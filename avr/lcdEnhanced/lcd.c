#define F_CPU 1000000UL /* Clock Frequency = 1Mhz */

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <string.h>

#define LCD_Port PORTD
#define RS PB0
#define EN PB2

#define DISPLAYLENGTH 16

long seconds=0;
char secCnt=0;
char myInterrupt=0;

// timer0 overflow interrupt
ISR(TIMER0_OVF_vect)
{
	if (++secCnt == 4) {
		secCnt = 0;
		seconds++;
		myInterrupt = 1;
	}
	TCNT0 = 0x12;
}

void register_timer();

void lcd_myinit(void);
void LCD_Init(void); 
void LCD_Command(unsigned char cmnd);
void LCD_Clear(void);
inline void LCD_Write(unsigned char data);
void LCD_Str(char *str);

void register_timer()
{
	// enable timer interrupts for timer0
	TIMSK = 0x01;
	// start value of timer. then starts from this value up to 255
	TCNT0 = 0x12;
	// clock-source + prescaling
	TCCR0 = 0x5;

	// enable interrupts
	sei();
}

void LCD_Clear(void)
{
	// clear display
	LCD_Command(0x01);
	_delay_ms(2);
	// cursor to home position
	LCD_Command(0x80);
}

void LCD_Command(unsigned char cmnd)
{
	LCD_Port = (LCD_Port & 0x0F) | (cmnd & 0xF0);/* Sending upper nibble */
	LCD_Port &= ~ (1<<RS);		/* RS=0, command reg. */
	LCD_Port |= (1<<EN);		/* Enable pulse */
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);
	_delay_us(200);

	LCD_Port = (LCD_Port & 0x0F) | (cmnd << 4);/* Sending lower nibble */
	LCD_Port |= (1<<EN);
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);
	_delay_ms(2);
}

void LCD_Init (void)  /* LCD Initialize function */
{
	DDRD = 0xFF;		/* Make LCD port direction as output */
	_delay_ms(20);		/* LCD Power ON delay always >15ms */
	
	LCD_Command(0x33);
	LCD_Command(0x32);	/* Send for 4 bit initialization of LCD  */
	LCD_Command(0x28);	/* 2 line, 5*7 matrix in 4-bit mode */
	LCD_Command(0x0c);	/* Display on cursor off */
	LCD_Command(0x06);	/* Increment cursor (shift cursor to right) */
	LCD_Command(0x01);	/* Clear display screen */
}

void LCD_Write(unsigned char data)
{
	LCD_Port = (LCD_Port & 0x0F) | (data & 0xF0);/* Sending upper nibble */
	LCD_Port |= (1<<RS);		/* RS=1, data reg. */
	LCD_Port|= (1<<EN);
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);
	_delay_us(200);

	LCD_Port = (LCD_Port & 0x0F) | (data << 4);/* Sending lower nibble */
	LCD_Port |= (1<<EN);
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);
	_delay_ms(2);
}

void LCD_Str(char *str)
{
	while (*str != 0) {
		LCD_Write(*str);
		str++;
	}
}

void lcd_myinit(void)
{
	LCD_Clear();
	LCD_Str("Uptime:");
}

void print_seconds()
{
	// next line
	LCD_Command(0xC0);

	char second[DISPLAYLENGTH+1] = {0};
	long tmpSeconds=seconds;
	int counter=0;

	do {
		// get last position and transform to ascii car
		char value = tmpSeconds % 10;
		value += 0x30;

		// 'print' last caracter to display
		second[DISPLAYLENGTH - (counter+1)] = value;

		tmpSeconds /= 10;
		counter++;
	} while (tmpSeconds);

	for (int i=DISPLAYLENGTH-counter; second[i] != 0; i++) {
		LCD_Write(second[i]);
		_delay_ms(100);
	}
}

int main() {
	register_timer();

	// portB is output, turn all LEDs off
	DDRB = 0xFF;
	PORTB = 0xFF;

	LCD_Init();
	lcd_myinit();

	// portA is input for switches
	DDRA = 0x00;

	while(1) {
		// check if clock changed - LCD rewrite
		if (myInterrupt) {
			myInterrupt = 0;
			print_seconds();
		}
	
		char aValue = PINA;
		if ((aValue & 0x01) == 0) {
			// switch0 pressed - reset timer
			seconds = 0;
			lcd_myinit();
			print_seconds();
		}

		_delay_ms(100);
	}
}
