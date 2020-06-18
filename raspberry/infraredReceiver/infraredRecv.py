#!/usr/bin/python3

# prerequisites on raspberry
# apt install lirc
# 	may fail; mv /etc/lirc/lirc_options.conf{.dist,}
# apt install lirc
# edit /etc/lirc_options.conf
	# driver=default
	# device=/dev/lirc0
# uncomment 'dtoverlay=gpio-ir, gpio_pin=XXX' in /boot/config.txt
# reboot, check whether gpio-ir is loaded and /dev/lirc0 exist
# mode2 -d /dev/lirc0 should start properly and print
# 	space 1726
# 	pulse 522
# repeatedly when pressing remote
# now get config for remote, either via irrecord tool or better, google for it
# ant put into /etc/lircd.conf.d/

# driver puts signal to /dev/lirc0
# lircd userspace daemon takes it, evaluate sit and puts to socket,
# usually in /var/run/lirc/lircd, try with nc -U /var/run/lirc/lircd
# python just reads this socket and prints

from lirc import RawConnection

def ProcessRawConnection(conn):
	keypress = None
	try:
		keypress = conn.readline(0.1)
	except Exception as e:
		return

	recv=keypress.split(" ")
	hexMsg=recv[0]
	amount=recv[1]	# how many times sent (button pressed longer)
	buttonid=recv[2]
	deviceName=recv[3] # as specified in /etc/lirc/lircd.conf
	print(keypress)

def infrared():
	conn = RawConnection()
	while True:
		ProcessRawConnection(conn)

infrared()
