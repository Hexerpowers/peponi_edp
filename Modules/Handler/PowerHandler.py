import json
import math
import sys
import time

import spidev


def get_battery_charge(voltage):
    val = int(math.floor((voltage - 41) * 14.29))
    if val <= 0:
        val = 0
    if val >= 100:
        val = 100
    return val


def update():
    global enabled, power_data, spi, prev_voltage, abnormal_counter
    data_stream = [0] * 12
    while enabled:
        try:
            time.sleep(0.01)
            try:
                tx_data = [0x04]
                data_stream.pop(0)
                data_stream.append(spi.xfer(tx_data)[0])

                if data_stream[0] == 255 and data_stream[1] == 255 and data_stream[2] == 255 and data_stream[
                        3] == 255 and data_stream[4] == 255 and data_stream[5] == 255:
                    data = [data_stream[6],
                            data_stream[7],
                            data_stream[8],
                            data_stream[9],
                            data_stream[10],
                            data_stream[11],
                            # data_stream[12]
                            ]

                    current_0 = round(((data[0] * 256 + data[1]) - 1750) / 18, 1)
                    current_1 = round(((data[2] * 256 + data[3]) - 1750) / 18, 1)
                    voltage = round((data[4] * 256 + data[5]) * 0.2296 / 16, 1)

                    state = 1
                    charge = get_battery_charge(round(voltage, 1))
                    if charge > 60:
                        state = 2

                    if prev_voltage - voltage > 5:
                        abnormal_counter += 1
                        if abnormal_counter > 5:
                            real_voltage = voltage
                            prev_voltage = voltage
                            abnormal_counter = 0
                        else:
                            real_voltage = prev_voltage
                    else:
                        abnormal_counter = 0
                        prev_voltage = voltage
                        real_voltage = voltage

                    # if int(data[12]) == 1:
                    #     state = 2

                    power_data = {
                        "state": state,
                        "current_0": current_0,
                        "current_1": current_1,
                        "voltage": real_voltage,
                        "charge": charge
                    }
            except Exception:
                print('||Подключение к устройству телеметрии питания утеряно.')
                power_data['state'] = 1
            print(json.dumps(power_data))
            sys.stdout.flush()
        except Exception:
            pass
        except KeyboardInterrupt:
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
    spi = spidev.SpiDev()
    spi.close()
    spi.open(0, 0)
    spi.lsbfirst = False
    spi.mode = 0b11
    spi.bits_per_word = 8
    spi.no_cs = True
    spi.max_speed_hz = 100000

    enabled = True

    prev_voltage = 0
    abnormal_counter = 0
    update()
except Exception as e:
    print('||Подключение к устройству телеметрии питания отсутствует.')
