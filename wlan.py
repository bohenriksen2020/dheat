import network
import time

SSID = "Guest"
PASSWORD = "11223344556677"

wlan = network.WLAN(network.STA_IF)

# Clean reset
wlan.active(False)
time.sleep(1)

wlan.active(True)
time.sleep(2)

"""# Scan networks
print("Scanning...")
nets = wlan.scan()

for net in nets:
    ssid = net[0].decode()
    rssi = net[3]
    auth = net[4]

    print(f"{ssid:30} RSSI={rssi:>3} dBm  auth={auth}")
"""
# Connect
print("\nConnecting to", SSID)
wlan.connect(SSID, PASSWORD)

for i in range(20):
    if wlan.isconnected():
        break
    print(".", end="")
    time.sleep(1)

print("\nConnected:", wlan.isconnected())

if wlan.isconnected():
    print("IP:", wlan.ifconfig())
else:
    print("WiFi status:", wlan.status())

