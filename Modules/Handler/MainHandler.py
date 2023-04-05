import math
import sys
import os
import time
from dronekit import connect, VehicleMode

import pythonping

from Modules.Handler.GuidedFlight import GuidedFlight

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from threading import Thread


class MainHandler:
    def __init__(self, config, st, lg):
        self.config = config
        self.st = st
        self.lg = lg
        self.main = Thread(target=self.main, daemon=True, args=())
        self.ping = Thread(target=self.ping, daemon=True, args=())
        self.vehicle = connect('/dev/ttyACM0', wait_ready=False, baud=57600)
        if self.vehicle.parameters['WP_YAW_BEHAVIOR'] != 0:
            self.vehicle.parameters['WP_YAW_BEHAVIOR'] = 0
        self.GF = GuidedFlight(st, lg, self.vehicle)

    def start(self):
        self.main.start()
        self.ping.start()
        self.GF.start()

    @staticmethod
    def get_battery_charge():
        return 100

    @staticmethod
    def get_power():
        return {
            "state": 1,
            "voltage": 25,
            "current": 0.5
        }

    def ping(self):
        while True:
            time.sleep(0.5)
            response_list = pythonping.ping(self.config['network']['controller_addr'], size=10, count=1, timeout=2000)
            self.st.set_ping(int(response_list.rtt_avg_ms))

    def main(self):
        while True:
            time.sleep(0.1)
            gui_ok = False
            tracking = self.st.get_tracking()
            if math.floor(time.time()) - tracking['gui_timestamp'] < 3:
                gui_ok = True
            self.st.set_runtime('comm_ok', gui_ok)
            self.st.set_battery_charge(self.get_battery_charge())
            self.st.set_power(self.get_power())
