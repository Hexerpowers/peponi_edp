import sys
import os
import time

import pythonping

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from threading import Thread
from Task.Executor import Executor


class Handler:
    def __init__(self, config, st, lg):
        self.config = config
        self.st = st
        self.lg = lg
        self.main = Thread(target=self.main, daemon=True, args=())
        self.aux = Thread(target=self.aux, daemon=True, args=())

    def start(self):
        self.main.start()
        self.aux.start()

    @staticmethod
    def get_charge():
        return 100

    def main(self):
        ex = Executor(self.config, self.st, self.lg).run()

    def aux(self):
        ping = 10
        while True:
            time.sleep(1)
            response_list = pythonping.ping(self.config['network']['base_url'], size=10, count=2, timeout=1)
            ping = response_list.rtt_avg_ms
            self.st.set_telemetry(self.get_charge(), ping)

