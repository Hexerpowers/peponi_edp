import json
import math
import os
import subprocess
import sys
import time

import pythonping
from dronekit import connect

from Modules.Handler.CameraHandler import CameraHandler
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
        self.power = Thread(target=self.power, daemon=True, args=())
        self.telemetry = Thread(target=self.telemetry, daemon=True, args=())

        self.CH = CameraHandler(st, lg)
        self.PH = None

        if self.st.config['general']['copter_mode'] == 'sim':
            self.vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)
        else:
            self.vehicle = connect('/dev/ttyACM0', wait_ready=False, baud=57600)

        self.GF = GuidedFlight(st, lg, self.vehicle)

    def start(self):
        self.main.start()
        self.ping.start()
        self.power.start()
        self.telemetry.start()
        self.CH.start()
        self.GF.start()

    def telemetry(self):
        while True:
            time.sleep(0.2)
            self.st.set_telemetry(
                {
                    "roll": math.degrees(float(self.vehicle.attitude.roll)),
                    "pitch": math.degrees(float(self.vehicle.attitude.pitch)),
                    "yaw": self.vehicle.heading,
                    "t_yaw": int(self.GF.get_target_yaw()),
                    "alt": int(self.vehicle.location.global_relative_frame.alt)+1 if int(
                        self.vehicle.location.global_relative_frame.alt) > 0 else 0
                }
            )

    def power(self):
        args = ["python3", "/home/" + self.config['general'][
            'platform_username'] + "/watchman_endpoint/Modules/Handler/PowerHandler.py"]
        self.PH = subprocess.Popen(args, stdout=subprocess.PIPE)
        while True:
            try:
                time.sleep(0.01)
                data = self.PH.stdout.readline()
                if len(data) < 4:
                    continue
                if "||" in str(data):
                    self.lg.error(data.decode(encoding='utf-8').replace('\n', "").replace('||', ""))
                    continue
                data = json.loads(data.decode(encoding='utf-8').replace('\n', ""))
                self.st.set_power(
                    {
                        "state": int(data['state']),
                        "current_0": float(data['current_0']) if float(data['current_0']) > 0 else 0,
                        "current_1": float(data['current_1']) if float(data['current_1']) > 0 else 0,
                        "voltage": float(data['voltage']),
                        "charge": int(data['charge']),
                    }
                )
            except Exception:
                pass

    def ping(self):
        while True:
            time.sleep(1)
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
            if math.floor(time.time()) - tracking['gui_timestamp'] < 3:
                gui_ok = True
            self.st.set_runtime('comm_ok', gui_ok)
