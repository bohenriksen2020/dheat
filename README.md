# ESP32 Floor Heating Balancing Tool

Small MicroPython project for an ESP32-WROOM-32D using 3 x DS18B20 temperature sensors to help balance underfloor heating loops.

---

## ✅ Status so far

We have successfully flashed MicroPython onto the ESP32.

Used command:

```bash
esptool --port /dev/tty.usbserial-0001 --baud 460800 write_flash 0x1000 ESP32_GENERIC-20260406-v1.28.0.bin
````

Board/firmware:

```text
ESP32-WROOM-32D
MicroPython ESP32_GENERIC v1.28.0
Serial port: /dev/tty.usbserial-0001
```

---

## 📥 Firmware download (official)

Download MicroPython firmware for ESP32 here:

👉 [https://micropython.org/download/esp32/](https://micropython.org/download/esp32/)

Direct link (latest generic firmware list):

👉 [https://micropython.org/resources/firmware/](https://micropython.org/resources/firmware/)

You want:

```text
ESP32_GENERIC-xxxx.bin
```

---

## 🎯 Goal

Measure:

| Sensor | Placement                            | Purpose               |
| ------ | ------------------------------------ | --------------------- |
| T1     | Manifold supply / fremløb            | Reference temperature |
| T2     | Manifold total return / samlet retur | System delta-T        |
| T3     | Return from the loop being tested    | Loop-specific delta-T |

The ESP32 will calculate:

```text
delta_system = supply - total_return
delta_loop   = supply - loop_return
```

And recommend:

| Delta loop | Meaning         | Action              |
| ---------- | --------------- | ------------------- |
| < 4°C      | Too much flow   | Close loop slightly |
| 5–7°C      | Good            | Leave as-is         |
| > 8–10°C   | Too little flow | Open loop slightly  |

---

## 🔧 Hardware needed

* ESP32-WROOM-32D
* 3 x DS18B20 waterproof temperature sensors
* 1 x 4.7kΩ resistor
* Jumper wires
* USB data cable (data-capable!)

---

## 🔌 Wiring

All DS18B20 sensors share the same data line.

| DS18B20 wire | ESP32  |
| ------------ | ------ |
| VCC          | 3.3V   |
| GND          | GND    |
| DATA         | GPIO 4 |

Add pull-up resistor:

```text
GPIO4 (DATA) ── 4.7kΩ ── 3.3V
```

---

## 🖥️ Install tools on Mac

```bash
pip3 install mpremote esptool
```

---

## 🔗 Connect to ESP32

Check port:

```bash
ls /dev/tty.*
```

Connect:

```bash
mpremote connect /dev/tty.usbserial-0001 repl
```

Test:

```python
print("ESP32 alive")
```

Exit:

```text
Ctrl + ]
```

---

## 🧠 Program

Create `main.py`:

```python
import machine
import onewire
import ds18x20
import time

PIN = 4

ow = onewire.OneWire(machine.Pin(PIN))
ds = ds18x20.DS18X20(ow)

roms = ds.scan()

print("Found sensors:")
for i, rom in enumerate(roms):
    print(i, rom)

if len(roms) < 3:
    print("ERROR: Expected 3 DS18B20 sensors")
    while True:
        time.sleep(5)

SUPPLY = 0
TOTAL_RETURN = 1
LOOP_RETURN = 2


def read_temps():
    ds.convert_temp()
    time.sleep_ms(750)
    return [ds.read_temp(rom) for rom in roms]


def recommendation(delta):
    if delta < 4:
        return "Too much flow -> close loop slightly"
    elif 4 <= delta <= 8:
        return "OK"
    else:
        return "Too little flow -> open loop slightly"


while True:
    temps = read_temps()

    supply = temps[SUPPLY]
    total_return = temps[TOTAL_RETURN]
    loop_return = temps[LOOP_RETURN]

    delta_system = supply - total_return
    delta_loop = supply - loop_return

    print("\n-----------------------------")
    print("Supply:       {:.1f} C".format(supply))
    print("Total return: {:.1f} C".format(total_return))
    print("Loop return:  {:.1f} C".format(loop_return))
    print("System ΔT:    {:.1f} C".format(delta_system))
    print("Loop ΔT:      {:.1f} C".format(delta_loop))
    print("Status:       {}".format(recommendation(delta_loop)))

    time.sleep(10)
```

---

## 📤 Upload program

```bash
mpremote connect /dev/tty.usbserial-0001 fs cp main.py :
mpremote connect /dev/tty.usbserial-0001 reset
```

---

## 🔍 Identify sensors

1. Touch one sensor
2. Watch which temperature rises
3. Assign indices:

```python
SUPPLY = X
TOTAL_RETURN = Y
LOOP_RETURN = Z
```

Re-upload:

```bash
mpremote connect /dev/tty.usbserial-0001 fs cp main.py :
mpremote connect /dev/tty.usbserial-0001 reset
```

---

## 🔄 Balancing workflow

1. Set supply temperature to **35–38°C**
2. Start pump
3. Open one loop
4. Place T3 on that loop
5. Wait for stabilization
6. Adjust:

   * ΔT < 4°C → close slightly
   * ΔT > 8°C → open more
7. Move to next loop
8. Repeat 2–3 rounds

---

## ⚠️ Notes

* Never close main return
* Make small adjustments (1/8 turn)
* Wait 10–15 min between changes
* System reacts slowly (thermal mass)

---

## 🧰 Useful commands

List files:

```bash
mpremote connect /dev/tty.usbserial-0001 fs ls
```

REPL:

```bash
mpremote connect /dev/tty.usbserial-0001 repl
```

Reset:

```bash
mpremote connect /dev/tty.usbserial-0001 reset
```

---

## 🚀 Next upgrades (optional)

* OLED display (live data)
* WiFi dashboard
* Logging to Home Assistant
* Alerts when ΔT is off

---

```

