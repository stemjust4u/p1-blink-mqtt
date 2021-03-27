import RPi.GPIO as GPIO 
from time import sleep 

GPIO.setwarnings(False)
pin = 10
GPIO.setmode(GPIO.BCM)  # BCM=GPIO (Broadcom), BOARD=1-40 board numbering
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW) 

while True: 
 GPIO.output(pin, GPIO.HIGH) 
 sleep(1) 
 GPIO.output(pin, GPIO.LOW) 
 sleep(1) 