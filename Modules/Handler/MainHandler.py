import json
import math
import os
import subprocess
import sys
import time

import pythonping
from dronekit import connect

from Modules.Common.Logger import Logger
from Modules.Handler.CameraHandler import CameraHandler
from Modules.Handler.GuidedFlight import GuidedFlight
from Modules.Store import Store

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from threading import Thread


class MainHandler:
    def __init__(self, config, st: Store, lg: Logger):
        self.config = config
        self.st = st
        self.lg = lg

        self.main = Thread(target=self.main, daemon=True, args=())
        self.ping = Thread(target=self.ping, daemon=True, args=())
        self.power = Thread(target=self.power, daemon=True, args=())
        self.telemetry = Thread(target=self.telemetry, daemon=True, args=())

        self.CH = CameraHandler(st, lg)
        self.PH = None

        self.initialized = False

        if self.st.config['general']['copter_mode'] == 'sim':
            self.vehicle = connect('tcp:192.168.137.1:5762', rate=20)
            self.initialized = True
        else:
            if os.path.exists('/dev/ttyACM0'):
                self.vehicle = connect('/dev/ttyACM0', wait_ready=True, baud=115200, rate=20)
                self.initialized = True
            else:
                self.lg.error("Полётный контроллер не обнаружен.")
                return

        self.GF = GuidedFlight(st, lg, self.vehicle)
        self.prev_gps_mode = False

    def start(self):
        self.main.start()
        self.ping.start()
        # self.power.start()
        self.telemetry.start()
        # self.CH.start()
        self.GF.start()

    @staticmethod
    def get_battery_charge(voltage):
        val = int(math.floor((voltage - 12) * 20.84))
        if val <= 0:
            val = 0
        if val >= 100:
            val = 100
        return val

    def telemetry(self):
        while True:
            time.sleep(0.04)
            try:
                self.st.set_telemetry(
                    {
                        "roll": round(math.degrees(float(self.vehicle.attitude.roll)), 2),
                        "pitch": round(math.degrees(float(self.vehicle.attitude.pitch)), 2),
                        "yaw": self.vehicle.heading,
                        "t_yaw": int(self.GF.get_target_yaw()),
                        "alt": int(self.vehicle.location.global_relative_frame.alt)+1 if int(
                            self.vehicle.location.global_relative_frame.alt) > 0 else 0,
                        "gps_sat": int(self.vehicle.gps_0.satellites_visible) if self.vehicle.gps_0.satellites_visible is not None else 0,
                        "actual_mode": str(self.vehicle.mode).split(":")[1]
                    }
                )
                self.st.set_power(
                    {
                        "state": 2,
                        "voltage": float(self.vehicle.battery.voltage),
                        "current_0": 0,
                        "current_1": 0,
                        "charge": self.get_battery_charge(float(self.vehicle.battery.voltage))
                    }
                )
            except Exception as e:
                pass

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
            if self.st.get_reboot_signal():
                os.system('pm2 restart 0')
            # self.st.set_power(
            #     {
            #         "state": 2 if float(self.vehicle.battery.voltage) > 46 else 1,
            #         "current_0": int(self.vehicle.battery.current),
            #         "current_1": 0,
            #         "voltage": float(self.vehicle.battery.voltage),
            #         "charge": int(int(self.vehicle.battery.level)*1.32),
            #     }
            # )
            # if self.st.get_gps_mode():
            #     if self.prev_gps_mode != self.st.get_gps_mode():
            #         self.vehicle.parameters['GPS_TYPE'] = 9
            #
            #         self.vehicle.parameters['EK3_SRC1_POSXY'] = 3
            #         self.vehicle.parameters['EK3_SRC1_POSZ'] = 1
            #         self.vehicle.parameters['EK3_SRC1_VELXY'] = 3
            #         self.vehicle.parameters['EK3_SRC1_VELZ'] = 3
            #         self.vehicle.parameters['EK3_SRC1_YAW'] = 1
            #
            #         self.vehicle.parameters['EK3_SRC2_POSXY'] = 3
            #         self.vehicle.parameters['EK3_SRC2_POSZ'] = 1
            #         self.vehicle.parameters['EK3_SRC2_VELXY'] = 3
            #         self.vehicle.parameters['EK3_SRC2_VELZ'] = 3
            #         self.vehicle.parameters['EK3_SRC2_YAW'] = 1
            #
            #         self.vehicle.parameters['EK3_SRC3_POSXY'] = 3
            #         self.vehicle.parameters['EK3_SRC3_POSZ'] = 1
            #         self.vehicle.parameters['EK3_SRC3_VELXY'] = 3
            #         self.vehicle.parameters['EK3_SRC3_VELZ'] = 3
            #         self.vehicle.parameters['EK3_SRC3_YAW'] = 1
            #         self.prev_gps_mode = self.st.get_gps_mode()
            # else:
            #     if self.prev_gps_mode != self.st.get_gps_mode():
            #         self.vehicle.parameters['GPS_TYPE'] = 0
            #
            #         self.vehicle.parameters['EK3_SRC1_POSXY'] = 0
            #         self.vehicle.parameters['EK3_SRC1_POSZ'] = 1
            #         self.vehicle.parameters['EK3_SRC1_VELXY'] = 5
            #         self.vehicle.parameters['EK3_SRC1_VELZ'] = 0
            #         self.vehicle.parameters['EK3_SRC1_YAW'] = 1
            #
            #         self.vehicle.parameters['EK3_SRC2_POSXY'] = 0
            #         self.vehicle.parameters['EK3_SRC2_POSZ'] = 1
            #         self.vehicle.parameters['EK3_SRC2_VELXY'] = 5
            #         self.vehicle.parameters['EK3_SRC2_VELZ'] = 0
            #         self.vehicle.parameters['EK3_SRC2_YAW'] = 1
            #
            #         self.vehicle.parameters['EK3_SRC3_POSXY'] = 0
            #         self.vehicle.parameters['EK3_SRC3_POSZ'] = 1
            #         self.vehicle.parameters['EK3_SRC3_VELXY'] = 5
            #         self.vehicle.parameters['EK3_SRC3_VELZ'] = 0
            #         self.vehicle.parameters['EK3_SRC3_YAW'] = 1
            #         self.prev_gps_mode = self.st.get_gps_mode()
