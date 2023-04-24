import math
import time
from threading import Thread

import smbus


class PowerHandler:

    def __init__(self, st, lg, addr):
        self.st = st
        self.lg = lg
        self.get_power = Thread(target=self.update, daemon=True, args=())
        self.power_data = {
            "state": 1,
            "current_0": 0,
            "current_1": 0,
            "voltage": 0
        }
        self.enabled = False
        try:
            self.bus = smbus.SMBus(1)
            self.addr = addr
            data = self.bus.read_i2c_block_data(self.addr, 0x00, 3)
            self.enabled = True
        except:
            self.lg.error('Нет устройства i2c по адресу ' + str(addr))

    def start(self):
        self.get_power.start()
        return self

    @staticmethod
    def get_battery_charge(voltage):
        val = int(math.floor((voltage - 36) * 6.94))
        if val <= 0:
            val = 0
        if val >= 100:
            val = 100
        return val

    def update(self):
        while self.enabled:
            time.sleep(0.5)
            while True:
                try:
                    data = self.bus.read_i2c_block_data(self.addr, 0x00, 3)
                    break
                except:
                    self.lg.error('Нет могу подключиться к устройству i2c по адресу ' + str(self.addr))
                    time.sleep(1)
            state = 1
            if self.get_battery_charge(round(int(data[2]) * 0.23, 1)) > 90:
                state = 2
            self.st.set_power(
                {
                    "state": state,
                    "current_0": data[0],
                    "current_1": data[1],
                    "voltage": round(int(data[2]) * 0.23, 1)
                }
            )
            self.st.set_battery_charge(self.get_battery_charge(round(int(data[2]) * 0.23, 1)))

    def __del__(self):
        while True:
            time.sleep(1)
            try:
                self.bus.close()
                break
            except:
                self.lg.error('Нет могу закрыть устройство i2c по адресу ' + str(self.addr))
