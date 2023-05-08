import json
import math
import time
import sys

import smbus
import signal


def handler(signum, frame):
    raise Exception("I2C read timeout")


def get_battery_charge(voltage):
    val = int(math.floor((voltage - 41) * 14.29))
    if val <= 0:
        val = 0
    if val >= 100:
        val = 100
    return val


def update():
    global enabled, power_data, bus, addr
    counter = 0
    while enabled:
        try:
            time.sleep(0.005)
            counter += 1
            try:
                data = bus.read_i2c_block_data(addr, 0x00, 6)
                current_0 = round(((data[0] * 256 + data[1]) - 1750) / 18, 1)
                current_1 = round(((data[2] * 256 + data[3]) - 1750) / 18, 1)
                voltage = round((data[4] * 256 + data[5]) * 0.2296 / 16, 1)
                state = 1
                charge = get_battery_charge(round(voltage, 1))
                if charge > 60:
                    state = 2
                power_data = {
                    "state": state,
                    "current_0": current_0,
                    "current_1": current_1,
                    "voltage": voltage,
                    "charge": charge
                }
            except Exception as e:
                print('||Не могу подключиться к устройству i2c по адресу ' + str(hex(addr)))
                power_data['state'] = 1
            if counter >= 100:
                print(json.dumps(power_data))
                sys.stdout.flush()
                counter = 0
        except Exception as e:
            pass
        except KeyboardInterrupt as e:
            break


power_data = {
    "state": 1,
    "current_0": 0,
    "current_1": 0,
    "voltage": 0,
    "charge": 0
}
enabled = False
try:
    bus = smbus.SMBus(1)
    addr = 0x22
    enabled = True
    update()
except Exception as e:
    print('||Нет i2c устройства телеметрии питания по адресу ' + str(hex(0x22)))
