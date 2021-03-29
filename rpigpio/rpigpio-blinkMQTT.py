import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
from os import path
from pathlib import Path
import re, json

GPIO.setwarnings(False)
pin = 10
GPIO.setmode(GPIO.BCM)  # BCM=GPIO (Broadcom), BOARD=1-40 board numbering
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

# Import mqtt and wifi info. Remove if hard coding in python file
home = str(Path.home())
with open(path.join(home, "stem"),"r") as f:
    stem = f.read().splitlines()

#=======   SETUP MQTT =================#
MQTT_SERVER = '10.0.0.115'                    # Replace with IP address of device running mqtt server/broker
MQTT_USER = stem[0]                           # Replace with your mqtt user ID
MQTT_PASSWORD = stem[1]                       # Replace with your mqtt password
MQTT_SUB_TOPIC1 = 'pi/led/instructions'       # Subscribe topic (incoming messages, instructions)
MQTT_PUB_TOPIC1 = 'pi/led/status'             # Publish topic (outgoing messages, data, instructions)
MQTT_CLIENT_ID = 'argon1'                     # Give your device a name
WIFI_SSID = stem[2]                           # Replace with your wifi SSID
WIFI_PASSWORD = stem[3]                       # Replace with your wifi password

#====== MQTT CALLBACK FUNCTIONS ==========#
# Each callback function needs to be 1) defined and 2) assigned/linked in main program below
# 3 Functions
# on_connect = Connect to the broker and subscribe to TOPICs
# on_message = When a message is received get the contents and assign it to a python dictionary (must be subscribed to the TOPIC)
# on_publish = Send a message to the broker

def on_connect(client, userdata, flags, rc):
    """ on connect callback verifies a connection established and subscribe to TOPICs"""
    print("attempting on_connect")
    if rc==0:
        mqtt_client.connected = True          # If rc = 0 then successful connection
        client.subscribe(MQTT_SUB_TOPIC1)     # Subscribe to topic
        print("Successful Connection: {0}".format(str(rc)))
        print("Subscribed to: {0}".format(MQTT_SUB_TOPIC1))
    else:
        mqtt_client.failed_connection = True  # If rc != 0 then failed to connect. Set flag to stop mqtt loop
        print("Unsuccessful Connection - Code {0}".format(str(rc)))

    ''' Code descriptions
        0: Successful Connection
        1: Connection refused: Unacceptable protocol version
        2: Connection refused: Identifier rejected
        3: Connection refused: Server unavailable
        4: Connection refused: Bad user name or password
        5: Connection refused: Not authorized '''

def on_message(client, userdata, msg):
    """on message callback will receive messages from the server/broker. Must be subscribed to the topic in on_connect"""
    global newmsg # can define global variables
    #print(msg.topic + ": " + str(msg.payload)) # Uncomment for debugging
    onoffD = json.loads(str(msg.payload.decode("utf-8", "ignore")))  # decode the msg to json and convert to python dictionary
    print(onfoffD)
    newmsg = True
    #onoff = onoffD['onoff']

def on_publish(client, userdata, mid):
    """on publish will send data to client"""
    #print("mid: " + str(mid)) # Uncomment for debugging
    pass

#==== start/bind mqtt functions ===========#
# Create a couple flags to handle a failed attempt at connecting. If our user/password is wrong we want to stop the loop.
mqtt.Client.connected = False          # Flag for initial connection (different than mqtt.Client.is_connected)
mqtt.Client.failed_connection = False  # Flag for failed initial connection
# Create our mqtt_client object and bind/link to our callback functions
mqtt_client = mqtt.Client(MQTT_CLIENT_ID) # Create mqtt_client object
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD) # Need user/password to connect to broker
mqtt_client.on_connect = on_connect    # Bind on connect
mqtt_client.on_message = on_message    # Bind on message
mqtt_client.on_publish = on_publish    # Bind on publish
mqtt_client.loop_start()               # Start monitoring loop as asynchronous. Starts a new thread and will process incoming/outgoing messages.
print("Connecting to: {0}".format(MQTT_SERVER))
mqtt_client.connect(MQTT_SERVER, 1883) # Connect to mqtt broker. This is a blocking function. Script will stop while connecting.
# Monitor if we're in process of connecting or if the connection failed
while not mqtt_client.connected and not mqtt_client.failed_connection:
    print("Waiting")
    sleep(1)
if mqtt_client.failed_connection:      # If connection failed then stop the loop and main program. Use the rc code to trouble shoot
    mqtt_client.loop_stop()
    sys.exit()

# MQTT setup is successful. Start the main program.
ledstatusD = {}
onoffD = {}
newmsg = False
while True:
    if newmsg and onoffD["onoff"] == 1:
        GPIO.output(pin, GPIO.HIGH)
        ledstatusD[str(pin) + 'i'] = 1
        ledstatusJSON = json.dumps(ledstatusD)
        mqtt_client.publish(MQTT_PUB_TOPIC1, ledstatusJSON)
        newmsg = False
    elif newmsg and onoffD["onoff"] == 0:
        GPIO.output(pin, GPIO.LOW)
        ledstatusD[str(pin) + 'i'] = 0
        ledstatusJSON = json.dumps(ledstatusD)
        mqtt_client.publish(MQTT_PUB_TOPIC1, ledstatusJSON)
        newmsg = False
    sleep(0.1)