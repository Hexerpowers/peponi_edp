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

    def start(self):
        self.main.start()

    def main(self):
        ex = Executor(self.config, self.st, self.lg).run()

