import network
import urequests as requests
import utime
from machine import Pin, ADC
import dht
import json
import ujson
from fastapi import FastAPI

# Konfiguration
SENSOR_PIN = 2
LDR_PIN = 0
API_URL = "http://localhost:8000/data"
WIFI_SSID = "ditt-wifi"
WIFI_PASSWORD = "ditt-lösenord"

# Initiera sensorer
dht_sensor = dht.DHT22(Pin(SENSOR_PIN))
ldr = ADC(LDR_PIN)


def connect_wifi():
    """Anslut till WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Ansluter till nätverk...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        # Vänta på anslutning
        for _ in range(20):
            if wlan.isconnected():
                break
            utime.sleep(1)

    print("Nätverkskonfiguration:", wlan.ifconfig())
    return wlan.isconnected()


def read_sensors():
    """Läs data från alla sensorer"""
    try:
        # Läs temperatur och fuktighet
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Läs ljusnivå (0-65535)
        light_raw = ldr.read_u16()
        light_percent = (light_raw / 65535) * 100

        return {
            "temperature": temperature,
            "humidity": humidity,
            "light_level": light_percent,
            "timestamp": utime.time(),
        }
    except Exception as e:
        print("Fel vid sensoravläsning:", e)
        return None


def send_data(data):
    """Skicka data till backend"""
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, data=ujson.dumps(data), headers=headers)

        if response.status_code == 200:
            print("Data skickad framgångsrikt")
        else:
            print(f"Fel vid sändning: {response.status_code}")

        response.close()
        return True
    except Exception as e:
        print("Fel vid dataöverföring:", e)
        return False


def main():
    """Huvudloop"""
    print("Startar väderstation...")

    if not connect_wifi():
        print("Kunde inte ansluta till WiFi")
        return

    while True:
        # Läs sensordata
        sensor_data = read_sensors()

        if sensor_data:
            print(
                f"Temp: {sensor_data['temperature']}°C, "
                f"Fukt: {sensor_data['humidity']}%, "
                f"Ljus: {sensor_data['light_level']:.1f}%"
            )

            # Skicka data till backend
            send_data(sensor_data)
        else:
            print("Kunde inte läsa sensordata")

        # Vänta 30 sekunder
        utime.sleep(30)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    main()
