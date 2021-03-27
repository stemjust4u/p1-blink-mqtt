"""This module builds an object containing multiple LEDs

The led bank allows the user to enter a list of GPIO pins,
set the pin numbering mode, and warnings flag. 
By default pins are initially set off (GPIO.LOW) but a 
'on' or 'off' argument can be passed on command line to 
modify the initial setting.
on/off methods can turn the list of leds on/off (LOW or HIGH). 

"""
import RPi.GPIO as GPIO 
import logging

class ledbank:
    """
    A class for the led bank

    ... 

    Attributes
    ----------
    pins : int (list)
        a list of integers representing the pins
    mode : str
        the pin mode. BCM (GPIO Broadcom convention)
                      BOARD (1-40 board convention)
        if BCM or BOARD is not entered the program exits
    warnings : bool
        can set warnings false to avoid extra output
    startas : str
        initial setting for led. Can be on or off

    Methods
    -------
    on
        Turns the list of leds on (GPIO.HIGH)
    off
        Turns the list of leds off (GPIO.LOW)
    """
    
    def __init__(self, pinlist, mode='BCM', startas="OFF", warnings=False):
        """
        Parameters
        pins : int (list)
            a list of integers representing the pins
        mode : str
            the pin mode. BCM (GPIO Broadcom convention)
                        BOARD (1-40 board convention)
            if BCM or BOARD is not entered the program exits
        warnings : bool
            can set warnings false to avoid extra output
        startas : str
            initial setting for led. Can be on or off
        """

        self.pins = [int(pin) for pin in pinlist] # Make sure pins are int using list comprehension
        if mode.upper() == 'BCM':
            GPIO.setmode(GPIO.BCM)  # BCM=GPIO (Broadcom)
        elif mode.upper() == 'BOARD':
            GPIO.setmode(GPIO.BOARD)  #BOARD=1-40 board numbering
        else:
            logging.info("invalid mode")
            exit()
        if type(warnings) == bool:
            GPIO.setwarnings(False)
        else:
            logging.info("invalid warning setting")
            exit()
        if startas.upper() == "OFF":
            for pin in self.pins:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        elif startas.upper() == "ON":
            for pin in self.pins:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
        else:
            logging.info("invalid initial setting")
            exit()

    def on(self):
        """ Turns leds on with GPIO.HIGH"""

        for pin in self.pins:
            GPIO.output(pin, GPIO.HIGH)

    def off(self):
        """ Turns leds off with GPIO.LOW"""

        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)


if __name__ == "__main__":
    from time import sleep
    logging.basicConfig(level=logging.DEBUG)
    pins = [26, 10]
    led = ledbank(pins, mode="BCM", startas="OFF")
    sleep(2)
    led.on()
    sleep(1)
    led.off()
