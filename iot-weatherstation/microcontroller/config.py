# Konfigurationsfil för microcontroller
CONFIG = {
    "wifi": {"ssid": "ditt-wifi-namn", "password": "ditt-lösenord"},
    "api": {"url": "http://din-server:8000/data", "timeout": 10},
    "sensors": {
        "dht_pin": 2,
        "ldr_pin": 0,
        "read_interval": 30,  # sekunder
    },
}
