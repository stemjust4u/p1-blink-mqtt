import rpigpio.led as led
import logging, sys, json
from os import path
from pathlib import Path
from time import sleep
import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to get variables. 
                                          # Set to INFO for status messages.
                                          # Set to CRITICAL to turn off

if len(sys.argv) == 2:                     # Using sys.argv to allow entering default state at the command line
    user_input = str(sys.argv[1])
else:
    user_input = "OFF"                     # Default LED state to OFF

pins = [26, 19]                            # Send a list of pins with LEDs
led = led.ledbank(pins, mode="BCM", startas=user_input) # BCM mode is GPIO number convention (vs 1-40 board number)

home = str(Path.home())                    # Import mqtt and wifi info. Remove if hard coding in python script
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
# on_connect = Connect to the broker and subscribe to TOPICs
# on_disconnect = Stop the loop and log the reason code
# on_message = When a message is received get the contents and assign it to a python dictionary (must be subscribed to the TOPIC)
# on_publish = Send a message to the broker

def on_connect(client, userdata, flags, rc):
    """ on connect callback verifies a connection established and subscribe to TOPICs"""
    logging.info("attempting on_connect")
    if rc==0:
        mqtt_client.connected = True          # If rc = 0 then successful connection
        client.subscribe(MQTT_SUB_TOPIC1)     # Subscribe to topic
        logging.info("Successful Connection: {0}".format(str(rc)))
        logging.info("Subscribed to: {0}\n".format(MQTT_SUB_TOPIC1))
    else:
        mqtt_client.failed_connection = True  # If rc != 0 then failed to connect. Set flag to stop mqtt loop
        logging.info("Unsuccessful Connection - Code {0}".format(str(rc)))

    ''' Code descriptions
        0: Successful Connection
        1: Connection refused: Unacceptable protocol version
        2: Connection refused: Identifier rejected
        3: Connection refused: Server unavailable
        4: Connection refused: Bad user name or password
        5: Connection refused: Not authorized '''

def on_message(client, userdata, msg):
    """on message callback will receive messages from the server/broker. Must be subscribed to the topic in on_connect"""
    global newmsg, incomingD
    if msg.topic == MQTT_SUB_TOPIC1:
        incomingD = json.loads(str(msg.payload.decode("utf-8", "ignore")))  # decode the json msg and convert to python dictionary
        newmsg = True
        # Debugging. Will print the JSON incoming payload and unpack the converted dictionary
        logging.debug("Receive: msg on subscribed topic: {0} with payload: {1}".format(msg.topic, str(msg.payload))) 
        logging.debug("Incoming msg converted (JSON->Dictionary) and unpacking")
        for key, value in incomingD.items():
            logging.debug("{0}:{1}".format(key, value))

def on_publish(client, userdata, mid):
    """on publish will send data to client"""
    #Debugging. Will unpack the dictionary and then the converted JSON payload
    logging.debug("msg ID: " + str(mid)) 
    logging.debug("Publish: Unpack outgoing dictionary (Will convert dictionary->JSON)")
    for key, value in outgoingD.items():
        logging.debug("{0}:{1}".format(key, value))
    logging.debug("Converted msg published on topic: {0} with JSON payload: {1}\n".format(MQTT_PUB_TOPIC1, json.dumps(outgoingD))) # Uncomment for debugging. Will print the JSON incoming msg
    pass 

def on_disconnect(client, userdata,rc=0):
    logging.debug("DisConnected result code "+str(rc))
    mqtt_client.loop_stop()

#==== start/bind mqtt functions ===========#
# Create a couple flags to handle a failed attempt at connecting. If user/password is wrong we want to stop the loop.
mqtt.Client.connected = False          # Flag for initial connection (different than mqtt.Client.is_connected)
mqtt.Client.failed_connection = False  # Flag for failed initial connection
# Create our mqtt_client object and bind/link to our callback functions
mqtt_client = mqtt.Client(MQTT_CLIENT_ID) # Create mqtt_client object
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD) # Need user/password to connect to broker
mqtt_client.on_connect = on_connect    # Bind on connect
mqtt_client.on_disconnect = on_disconnect    # Bind on disconnect
mqtt_client.on_message = on_message    # Bind on message
mqtt_client.on_publish = on_publish    # Bind on publish
logging.info("Connecting to: {0}".format(MQTT_SERVER))
mqtt_client.connect(MQTT_SERVER, 1883) # Connect to mqtt broker. This is a blocking function. Script will stop while connecting.
mqtt_client.loop_start()               # Start monitoring loop as asynchronous. Starts a new thread and will process incoming/outgoing messages.
# Monitor if we're in process of connecting or if the connection failed
while not mqtt_client.connected and not mqtt_client.failed_connection:
    logging.info("Waiting")
    sleep(1)
if mqtt_client.failed_connection:      # If connection failed then stop the loop and main program. Use the rc code to trouble shoot
    mqtt_client.loop_stop()
    sys.exit()

# MQTT setup is successful. Initialize dictionaries and start the main loop.
outgoingD = {}
incomingD = {}
led.on()
sleep(1)
led.off()  # Blink LED once

newmsg = False
while True:
    if newmsg:                                 # INCOMING: New msg/instructions have been received
        if incomingD["onoff"] == 1:
            led.on()                                        # Turn on LED (set it HIGH)
            outgoingD['ledbank' + 'i'] = 1                  # The i tells node-red an integer is being sent. Will see the check in the node-red MQTT parse function.
        elif incomingD["onoff"] == 0:
            led.off()                                       # Turn off LED (set it LOW)
            outgoingD['ledbank' + 'i'] = 0                  # The i tells node-red an integer is being sent. Will see the check in the node-red MQTT parse function.
        else:
            outgoingD['ledbank' + 'i'] = 99                 # Update LED status to 99 for unknown
                                               # OUTGOING: Convert python dictionary to JSON and publish
        mqtt_client.publish(MQTT_PUB_TOPIC1, json.dumps(outgoingD)) 
        newmsg = False                                      # Reset the new msg flag