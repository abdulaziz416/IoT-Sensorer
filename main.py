import network
import time
import dht
from machine import Pin
import urequests


SSID = "Redom"
PASSWORD = "1234"
API_KEY = "DIN_THINGSPEAK_WRITE_API_KEY" 
DHT_PIN = 15  


sensor = dht.DHT11(Pin(DHT_PIN))


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Ansluter till Wi-Fi...")
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print("Väntar på anslutning...")
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('Kunde inte ansluta till Wi-Fi')
else:
    print('Ansluten! IP-adress:', wlan.ifconfig()[0])


while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        
        print(f"Mätning: {temp}°C, {hum}%")

        
        url = f"http://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={hum}"
        
       
        response = urequests.get(url)
        
        if response.text == "0":
            print("Fel: ThingSpeak tog inte emot datan.")
        else:
            print(f"Data skickad! (Entry ID: {response.text})")
            
        response.close() 

    except OSError as e:
        print("Kunde inte läsa sensorn eller nätverksfel:", e)
    time.sleep(20)
