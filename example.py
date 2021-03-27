import rpigpio.led as led
import logging, sys
from time import sleep

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) == 2:
    user_input = str(sys.argv[1])
else:
    user_input = "OFF"

pins = [26, 10]
led = led.ledbank(pins, mode="BCM", startas=user_input)
sleep(2)
led.on()
sleep(1)
led.off()