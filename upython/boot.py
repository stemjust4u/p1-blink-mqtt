from time import sleep
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

with open("stem", "rb") as f:
  user_info = f.read().splitlines()
MQTT_SERVER = '10.0.0.115'
MQTT_USER = user_info[0] 
MQTT_PASSWORD = user_info[1] 
MQTT_SUB_TOPIC1 = b'esp32/led/instructions'
MQTT_PUB_TOPIC1 = b'esp32/led/status'
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
WIFI_SSID = user_info[2]
WIFI_PASSWORD = user_info[3]
    
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(WIFI_SSID, WIFI_PASSWORD)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())