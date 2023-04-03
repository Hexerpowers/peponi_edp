import math
import sys
import os
import time
# from dronekit import connect, VehicleMode

import pythonping

# from Modules.Handler.GuidedFlight import GuidedFlight

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
        #self.vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=57600)
        #self.GF = GuidedFlight(st, lg, self.vehicle)

    def start(self):
        self.main.start()
        #self.GF.start()

    def main(self):
        while True:
            time.sleep(0.01)

            gui_ok = False
            hank_ok = False
            tracking = self.st.get_tracking()
            if math.floor(time.time()) - tracking['gui_timestamp'] < 3:
                gui_ok = True
            if math.floor(time.time()) - tracking['hank_timestamp'] < 3:
                hank_ok = True

            self.st.set_runtime('comm_ok', gui_ok)

            response_list = pythonping.ping('127.0.0.1', size=10, count=1, timeout=2000)
            ping = int(response_list.rtt_avg_ms)
            self.st.set_ping(ping)





