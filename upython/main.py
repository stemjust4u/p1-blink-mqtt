from machine import Pin
from time import sleep
#led1 = Pin(5, Pin.OUT)
led2 = Pin(2, Pin.OUT) #2 is the internal LED

#led1.value(0)
led2.value(1)


while True:
    #led1.value(not led1.value())
    led2.value(not led2.value())
    print("led2", led2.value())
    sleep(0.5)