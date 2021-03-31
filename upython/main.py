from machine import Pin, ADC
from time import time, sleep
import ujson

print("in main")

def sub_cb(topic, msg):
  #print("sub cd function %s %s %s" % (topic, msg, MQTT_SUB_TOPIC1))
  global newmsg, onoffD
  if topic == MQTT_SUB_TOPIC1:
    #print('ESP received message')
    onoffD = ujson.loads(msg.decode("utf-8", "ignore")) # decode json data to dictionary
    newmsg = True
    
def connect_and_subscribe():
  global MQTT_CLIENT_ID, MQTT_SERVER, MQTT_SUB_TOPIC1, MQTT_USER, MQTT_PASSWORD
  client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, user=MQTT_USER, password=MQTT_PASSWORD)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(MQTT_SUB_TOPIC1)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (MQTT_SERVER, MQTT_SUB_TOPIC1))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

# MQTT setup is successful.
# Publish generic status confirmation easily seen on MQTT Explorer
# Initialize dictionaries and start the main loop.
client.publish(b"status", b"esp32 connected, entering main loop")
pin = 2
led = Pin(pin, Pin.OUT) #2 is the internal LED
ledstatusD = {}
onoffD = {}
onoffD["onoff"] = 0
newmsg = True
while True:
    try:
      client.check_msg()
      if newmsg and onoffD["onoff"] == 1:                # Received new msg turning LED on (on=1)
        led.value(1)                                     # Turn on LED (set it to 1)
        ledstatusD[str(pin) + 'i'] = 1                   # Update LED status for sending via mqtt
        ledstatusJSON = ujson.dumps(ledstatusD)          # Convert python dictionary to json
        client.publish(MQTT_PUB_TOPIC1, ledstatusJSON)   # Publish LED status
        newmsg = False
      elif newmsg and onoffD["onoff"] == 0:              # Received new msg turning LED off (off=0)
        led.value(0)                                     # Turn off LED (set it to 0)
        ledstatusD[str(pin) + 'i'] = 0
        ledstatusJSON = ujson.dumps(ledstatusD)
        client.publish(MQTT_PUB_TOPIC1, ledstatusJSON)
        newmsg = False
      sleep(0.1)
    except OSError as e:
      restart_and_reconnect()