from machine import Pin, ADC
import utime, ujson, micropython, ubinascii, network, gc
from umqttsimple import MQTTClient
gc.collect()
micropython.alloc_emergency_exception_buf(100)

def connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(WIFI_SSID, WIFI_PASSWORD)

    while station.isconnected() == False:
        pass

    print('Connection successful')
    print(station.ifconfig())

def mqtt_setup(IPaddress):
    global MQTT_CLIENT_ID, MQTT_SERVER, MQTT_USER, MQTT_PASSWORD, MQTT_SUB_TOPIC
    with open("stem", "rb") as f:    # Remove and over-ride MQTT/WIFI login info below
      stem = f.read().splitlines()
    MQTT_SERVER = IPaddress   # Over ride with MQTT/WIFI info
    MQTT_USER = stem[0]         
    MQTT_PASSWORD = stem[1]
    WIFI_SSID = stem[2]
    WIFI_PASSWORD = stem[3]
    MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
    MQTT_SUB_TOPIC = b'esp32/led/instructions'
    
def mqtt_connect_subscribe():
    global MQTT_CLIENT_ID, MQTT_SERVER, MQTT_SUB_TOPIC, MQTT_USER, MQTT_PASSWORD
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.set_callback(mqtt_on_message)
    client.connect()
    print('(CONNACK) Connected to {0} MQTT broker'.format(MQTT_SERVER))
    client.subscribe(MQTT_SUB_TOPIC)
    print('Subscribed to {0}'.format(MQTT_SUB_TOPIC)) 
    return client

def mqtt_on_message(topic, msg):
    global mqtt_incomingD, mqtt_newmsg
    print("on_message Received - topic:{0} payload:{1}".format(topic, msg.decode("utf-8", "ignore")))
    if topic == MQTT_SUB_TOPIC:
        mqtt_newmsg = True
        mqtt_incomingD = ujson.loads(msg.decode("utf-8", "ignore")) # decode json data to dictionary
        for key, value in mqtt_incomingD.items():  # Unpack the dictionary for debugging purposes
            print('on_message Dict key:{0} value:{1}'.format(key, value))
            
def mqtt_reset():
    print('Failed to connect to MQTT broker. Reconnecting...')
    utime.sleep_ms(5000)
    machine.reset()

def main():
    global mqtt_incomingD, mqtt_newmsg
    
    #===== SETUP MQTT/DEBUG VARIABLES ============#
    # Setup mqtt variables (topics and data containers) used in on_message, main loop, and publishing
    mqtt_setup('10.0.0.115')
    MQTT_PUB_TOPIC = b'esp32/led/status' # Topic for publish led status to mqtt broker
    mqtt_incomingD = {}
    mqtt_incomingD['onoff'] = 0
    mqtt_newmsg = False
    outgoingD = {} # container used for publishing the mqtt data
    
    # Connect and create the client
    try:
        mqtt_client = mqtt_connect_subscribe()
    except OSError as e:
        mqtt_reset()
    # MQTT setup is successful, publish status msg that can easily be seen on MQTT Exporer to confirm connection
    mqtt_client.publish(b'esp32/led/status', b'esp32 connected, entering main loop')
    
    # Initialize flags and timers
    checkmsgs = False
    sendmsgs = False
    t0onmsg_ms = utime.ticks_ms()
    on_msg_timer_ms = 100 # How frequently to check for msg (ms)
    pin = 2
    led = Pin(pin, Pin.OUT) # 2 is the internal LED
    led.value(1)
    utime.sleep_ms(1000)
    led.value(0)  # flash led 
    
    while True:
        try:
            if utime.ticks_diff(utime.ticks_ms(), t0onmsg_ms) > on_msg_timer_ms:
                checkmsgs = True
                t0onmsg_ms = utime.ticks_ms()
            
            if checkmsgs:
                mqtt_client.check_msg()
                if mqtt_newmsg:
                    led.value(mqtt_incomingD['onoff'])  # Set the LED on or off based on mqtt msg from nodered
                    mqtt_newmsg = False
                    # Update outgoingD to tell nodered what state the LED is in. Nodered dashboard will update
                    outgoingD[str(pin) + 'i'] = led.value() # The i tells node-red an integer is being sent. Will see the check in the node-red MQTT parse function.
                    sendmsgs = True
                checkmsgs = False
                
            if sendmsgs:
                mqtt_client.publish(MQTT_PUB_TOPIC, ujson.dumps(outgoingD)) # Use ujson to convert Python dict to JSON and publish
                print('Published msg {0} with payload {1}'.format(MQTT_PUB_TOPIC, ujson.dumps(outgoingD)))
                sendmsgs = False
                
        except OSError as e:
            mqtt_reset()

if __name__ == "__main__":
    # Run main loop            
    main()
