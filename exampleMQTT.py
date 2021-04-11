#!/usr/bin/env python3
'''
Project that builds on previous LED code.
- Adds importing the led package previously created
- Adds mqtt communication to a remote Pi with node-red to allow turning the led on/off and displaying the status

'''

import rpigpio.led as led        # Import the rpigpio.led module we created
from time import sleep

import logging                   # Used for debugging. Allows print statements to be easily enabled or disabled
import paho.mqtt.client as mqtt
import sys, json                 # Used for mqtt
from os import path              # Used for mqtt
from pathlib import Path         # Used for mqtt

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

def get_command_line_input(cli_input):        # Using sys.argv to allow entering default state at the command line
    if len(cli_input) == 2:                   # First element of array is the program name. If there is a second element then user entered default state
        default_state = str(cli_input[1])
    else:
        default_state = "OFF"                 # Default LED state to OFF
    return default_state

def get_login_info(file):
    home = str(Path.home())                    # Import mqtt and wifi info. Remove if hard coding in python script
    with open(path.join(home, file),"r") as f:
        user_info = f.read().splitlines()
    return user_info

def main():
    ''' define global variables '''
    global mqtt_client, outgoingD, incomingD, newmsg
    global MQTT_SUB_TOPIC1, MQTT_PUB_TOPIC1           # Can add more topics for subscribing/publishing
    global led

    #==== LOGGING/DEBUGGING ============#
    # Logging package allows you to easiliy turn print-like statements on/off GLOBALLY with 'level' settings below
    # Using basicConfig logging at root level. The 'level', on/off, controls other modules with logging enabled.
    logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to get variables and status messages. 
                                              # Set to INFO for status messages only.
                                              # Set to CRITICAL to turn off

    default_state = get_command_line_input(sys.argv) # Get default state when script is executed from command line

    #==== HARDWARE SETUP ===============# 
    pins = [26, 19]                            # Send a list of pins with LEDs
    led = led.ledbank(pins, mode="BCM", startas=default_state) # BCM mode is GPIO number convention (vs 1-40 board number)

    #====   SETUP MQTT =================#
    user_info = get_login_info("stem")
    MQTT_SERVER = '10.0.0.115'                    # Replace with IP address of device running mqtt server/broker
    MQTT_USER = user_info[0]                      # Replace with your mqtt user ID
    MQTT_PASSWORD = user_info[1]                  # Replace with your mqtt password
    MQTT_SUB_TOPIC1 = 'pi/led/instructions'       # Subscribe topic (incoming messages, instructions)
    MQTT_PUB_TOPIC1 = 'pi/led/status'             # Publish topic (outgoing messages, data, instructions)
    MQTT_CLIENT_ID = 'argon1'                     # Give your device a name
    WIFI_SSID = user_info[2]                      # Replace with your wifi SSID
    WIFI_PASSWORD = user_info[3]                  # Replace with your wifi password

    #==== START/BIND MQTT FUNCTIONS ====#
    # Create a couple flags in the mqtt.Client class to handle a failed attempt at connecting. If user/password is wrong we want to stop the loop.
    mqtt.Client.connected = False          # Flag for initial connection
    mqtt.Client.failed_connection = False  # Flag for failed initial connection
    # Create our mqtt_client object and bind/link to our callback functions
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)             # Create mqtt_client object
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD) # Need user/password to connect to broker
    mqtt_client.on_connect = on_connect                   # Bind on connect
    mqtt_client.on_disconnect = on_disconnect             # Bind on disconnect
    mqtt_client.on_message = on_message                   # Bind on message
    mqtt_client.on_publish = on_publish                   # Bind on publish
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

    #==== MAIN LOOP ====================#
    # MQTT setup is successful. Initialize dictionaries and start the main loop.
    outgoingD, incomingD = {}, {}
    led.on()
    sleep(1)
    led.off()  # Blink LED once to notify main loop starting
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

if __name__ == "__main__":     # Will run main() code when program is executed as a script (vs imported as a module)
    main()