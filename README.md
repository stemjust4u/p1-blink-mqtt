# [STEM Just 4 U Home Page](https://stemjust4u.com/)
# This project builds on P1-blink (multiple methods to turn an LED on/off with Raspberry Pi and ESP32.) by adding MQTT/node-red functions

[Link to MQTT Project Web Site](https://stemjust4u.com/p1-Led-Blink-MQTT)  
[Link to initial LED Project](https://stemjust4u.com/p1-Led-Blink)
## Materials 
* LED (1.7-3V/20mA LED)
* Resistor (75-100ohm) - controls current going to LED
* Raspberry Pi and/or esp32 as remote mosquitto clients
* Raspberry Pi as mosquitto server (broker) and node-red server (note - the RPi being used to control an LED can also be used as the server. The mqtt client and server can be on the same Pi)

This is a continuation of the LED blink project. Adding MQTT (will be using mosquitto) to practice communicating between remote devices/clients (esp32/Pi) and a server (broker) Pi running mosquitto/node-red.  (link to mqtt/node-red setup)

![MQTT/node-red](images/pi-mqtt-node-red-diagram.jpg "Diagram")

The esp32 (mosquitto client) will run micropython with umqttsimple to send the LED status and receive on/off instructions.

The RPi (mosquitto client) will run python with Paho to send the LED status and receive on/off instructions.

The Pi server will have a mosquitto/node-red server running. Node-red will be used to display the LED status and to send on/off instructions. The Pi server will be the communication hub between the remote esp32/RPi and node-red.

To access the Pi server node-red configuration and LED status (dashboard) you use a web browser. (PiserverIPaddress:1880 and PiserverIPaddress:1880/ui)

>A quick check that your LED is working can be done by connecting it to the 3.3V pin on your Pi.

# Connecting the LED to Raspberry Pi
A great resource for Raspberry Pi pins is pinout.xyz. You can use a breadboard or connect the LED/resistor directly with jumper wires.
For my setup I used two LEDs and GPIO10 and 26. (along with GRND) Start with a single LED and get it working first.

# Connecting LED to esp32
On the ESP32 I used the internal LED (pin2). Although you could connect an external LED and just change the pin.  
You load the upython script on to the esp32 as /main.py  [Directions using Thonny](https://stemjust4u.com/esp32-esp8266)

# General Work Flow
## Mosquitto (mqtt) Clients
>Python/uPython
MQTT setup section where you define the wifi SSID/password and MQTT user/password info needed for the client to send/publish messages to the MQTT server/broker.  (if RPi is already connected to the network the wifi SSID/password is not necessary)

>Define MQTT callback functions - multiple functions are required to handle the mqtt communications (I use JSON for messages). Connect function to connect to the mqtt server(broker). Message function to handle receiving messages/instructions from the broker. Publish function to handle sending/publishing messages to the broker.
Start/bind MQTT functions - Bind the MQTT callback functions to mqtt client.

>MAIN loop - ie where you take action based on instructions sent from the broker and send status update back to it. To make the messaging scaleable I use dictionaries in python and JSON for the mqtt message. An easy way to convert beetween the two is json.dumps/loads (or ujson.dumps/loads for uPython). For receiving messages the json.loads is used to convert from JSON to python dictionary. For publishing messages the json.dumps is used to convert from python dictionary to JSON.

## Mosquitto (mqtt) Broker/Node-red Server
>MQTT server just needs to be running (no python code necessary)
Node-red Server - Setup nodes (can use JavaScript) for receiving mqtt messages (in JSON format) from the clients. Based on these messages can update the dashboard and write to an influxdb. Can also send messages back to the clients giving them instructions.

---

To avoid posting my wifi ID/password on github I put the information in a local file and read it into a list. Be careful with case sensitivity. I found out Paho (python3) was not case sensitive to the wifi SSID. But umqttsimple (upython) was case sensitive.

---

MQTT Explorer is a great tool for watching messages between your clients and broker. You can also manually enter a topic and send a msg to test your code. This is useful for first setting up your code and trouble shooting.

![MQTT Explorer](images/MQTT-explorer.png "MQTT Explorer")

# Code
​​There are 3 sections
1. Single LED with RPi(Python) - /rpigpio/rpigpio-blinkMQTT.py
2. Multiple LED with RPi(Python) - /example.py (led module is imported from /rpigpio)
3. Single LED with esp32(uPython) - /upython (requires boot, main, and umqttsimple)

# Node Red
The node-red flow can be imported below. (and images of the flow are above). 
> mqtt in node is used to listen for messages from the clients (server: localhost:1883 and enter the topic)

> I use a JavaScript function to parse the incoming message. This allows me to have a generic script I use in any node-red setup. Code is in node-red folder. The JSON object is parsed and fields are created for each item. The msg topic is broken into a tag. An identifier is used on the end to indicate if the value was a float or integer ('f' vs 'i' is added to the end of the items in the python/upython code). 

# More Code (multi LEDs with a Class object)
LED class (object)

/example.py  
|- rpigpio (packge/folder)  
|         |-- __init_.py  
|         |-- led.py (module)  

​​The rpigpio package (folder) contains a __init__.py and led.py module  
The led.py module can be executed standalone ($ python3 led.py) for testing.  
If you wanted to have this program start up at boot as a systemd service the logging function could be used for trouble shooting.  

The example.py script can be ran with  
`$ python3 example.py`  
Or an intial ON or OFF state can be passed (that is the sys.argv portion)  
`$ python3 example.py ON`