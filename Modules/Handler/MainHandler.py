import math
import os
import sys
import time

import pythonping
from dronekit import connect

from Modules.Handler.CameraHandler import CameraHandler
from Modules.Handler.GuidedFlight import GuidedFlight
from Modules.Handler.PowerHandler import PowerHandler

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

        self.PH = PowerHandler(st, lg, 0x22)
        self.CH = CameraHandler(st, lg)

        self.vehicle = connect('/dev/ttyACM0', wait_ready=False, baud=57600)
        if self.vehicle.parameters['LAND_SPEED'] != 30:
            self.vehicle.parameters['LAND_SPEED'] = 30

        self.GF = GuidedFlight(st, lg, self.vehicle)

    def start(self):
        self.main.start()
        self.ping.start()
        self.PH.start()
        self.CH.start()
        self.GF.start()

    def get_attitude(self):
        return {
            "roll": math.degrees(float(self.vehicle.attitude.roll)),
            "pitch": math.degrees(float(self.vehicle.attitude.pitch)),
            "yaw": self.vehicle.heading,
            "t_yaw": int(self.GF.get_target_yaw()),
            "alt": int(self.vehicle.location.global_relative_frame.alt) if int(
                self.vehicle.location.global_relative_frame.alt) > 0 else 0
        }

    def ping(self):
        while True:
            time.sleep(2)
            try:
                response_list = pythonping.ping(self.st.get_controller_address(), size=20, count=2,
                                                timeout=2)
                self.st.set_ping(int(response_list.rtt_avg_ms))
            except Exception as e:
                self.lg.error(e)

    def main(self):
        while True:
            time.sleep(0.25)
            gui_ok = False
            tracking = self.st.get_tracking()
            if math.floor(time.time()) - tracking['gui_timestamp'] < 5:
                gui_ok = True
            self.st.set_runtime('comm_ok', gui_ok)

            self.st.set_telemetry(self.get_attitude())
