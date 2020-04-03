#define F_CPU 1000000UL /* Clock Frequency = 1Mhz */

#include <util/delay.h>
#include <avr/io.h>
#include <stdlib.h>
#include <string.h>

#define LCD_Port PORTD
#define RS PB0
#define EN PB2

void LCD_Init(void); 
void LCD_Command(unsigned char cmnd);
void LCD_Clear(void);
void LCD_Write(unsigned char data);

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
	DDRD = 0xFF;		/* Make LCD port direction as o/p */
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

int main() {
	LCD_Init();
	LCD_Clear();
	LCD_Str("hallo");

	while(1);
}
