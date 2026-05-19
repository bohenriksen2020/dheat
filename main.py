import machine
import onewire
import ds18x20
import time

# -----------------------------
# CONFIG
# -----------------------------

DATA_PIN = 4
READ_INTERVAL_SECONDS = 10

# Target delta-T for one floor heating loop
DELTA_LOW = 4.0
DELTA_OK_LOW = 5.0
DELTA_OK_HIGH = 7.0
DELTA_HIGH = 9.0

# Update these after sensor identification
SUPPLY_SENSOR = 0
TOTAL_RETURN_SENSOR = 1
LOOP_RETURN_SENSOR = 2


# -----------------------------
# SETUP
# -----------------------------

ow = onewire.OneWire(machine.Pin(DATA_PIN))
ds = ds18x20.DS18X20(ow)

roms = ds.scan()

print("")
print("Delta Heat starting...")
print("Found DS18B20 sensors:")

for index, rom in enumerate(roms):
    print(index, rom)

if len(roms) < 3:
    print("")
    print("ERROR: Expected 3 sensors.")
    print("Check wiring:")
    print("- VCC to 3.3V")
    print("- GND to GND")
    print("- DATA to GPIO", DATA_PIN)
    print("- 4.7k resistor between DATA and 3.3V")
    while True:
        time.sleep(5)


# -----------------------------
# FUNCTIONS
# -----------------------------

def read_temperatures():
    ds.convert_temp()
    time.sleep_ms(750)

    temps = []

    for rom in roms:
        temp = ds.read_temp(rom)
        temps.append(temp)

    return temps


def classify_delta(delta):
    if delta < DELTA_LOW:
        return "TOO MUCH FLOW - close loop slightly"

    if DELTA_OK_LOW <= delta <= DELTA_OK_HIGH:
        return "OK - leave loop as-is"

    if delta > DELTA_HIGH:
        return "TOO LITTLE FLOW - open loop slightly"

    return "ACCEPTABLE - small adjustment optional"


def print_sensor_identification(temps):
    print("")
    print("Sensor identification:")
    for index, temp in enumerate(temps):
        print("Sensor {}: {:.1f} C".format(index, temp))


def print_report(temps):
    supply = temps[SUPPLY_SENSOR]
    total_return = temps[TOTAL_RETURN_SENSOR]
    loop_return = temps[LOOP_RETURN_SENSOR]

    delta_system = supply - total_return
    delta_loop = supply - loop_return

    print("")
    print("================================")
    print("DELTA HEAT")
    print("================================")
    print("Supply:        {:.1f} C".format(supply))
    print("Total return:  {:.1f} C".format(total_return))
    print("Loop return:   {:.1f} C".format(loop_return))
    print("--------------------------------")
    print("System delta:  {:.1f} C".format(delta_system))
    print("Loop delta:    {:.1f} C".format(delta_loop))
    print("--------------------------------")
    print("Recommendation:")
    print(classify_delta(delta_loop))
    print("================================")


# -----------------------------
# MAIN LOOP
# -----------------------------

while True:
    try:
        temps = read_temperatures()

        print_sensor_identification(temps)
        print_report(temps)

    except Exception as error:
        print("")
        print("ERROR reading sensors:")
        print(error)

    time.sleep(READ_INTERVAL_SECONDS)
