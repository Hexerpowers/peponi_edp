from threading import Thread

import smbus
import time


class PowerHandler:

    def __init__(self, st, lg, addr):
        self.st = st
        self.lg = lg
        self.get_power = Thread(target=self.update, daemon=True, args=())
        self.power_data = {
            "state":1,
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
            self.lg.error('Нет устройства i2c по адресу '+str(addr))

    def start(self):
        self.get_power.start()
        return self

    @staticmethod
    def get_battery_charge(voltage):
        return (voltage-18)*13.8

    def update(self):
        while self.enabled:
            time.sleep(0.5)
            while True:
                try:
                    data = self.bus.read_i2c_block_data(self.addr, 0x00, 3)
                    break
                except:
                    self.lg.error('Нет могу подключиться к устройству i2c по адресу '+str(self.addr))
                    time.sleep(1)
            state = 1
            if self.get_battery_charge(data[2]) > 20:
                state = 2
            self.st.set_power(
                {
                    "state": state,
                    "current_0": data[0],
                    "current_1": data[1],
                    "voltage": data[2]
                }
            )
            self.st.set_battery_charge(self.get_battery_charge(data[2]))

    def __del__(self):
        while True:
            time.sleep(1)
            try:
                self.bus.close()
                break
            except:
                self.lg.error('Нет могу закрыть устройство i2c по адресу '+str(self.addr))
