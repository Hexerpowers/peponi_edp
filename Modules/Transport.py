import json
import time
from threading import Thread

import requests


class Transport:
    def __init__(self, config, st, lg):
        self.config = config
        self.st = st
        self.lg = lg
        self.position_loop = Thread(target=self.position, daemon=True, args=())
        self.runtime_loop = Thread(target=self.runtime, daemon=True, args=())

    def start(self):
        self.position_loop.start()
        self.runtime_loop.start()

    def position(self):
        got_once = False
        raw_response = "{}"
        parsed_response = {}
        req_interval = float(self.config['general']['req_interval'])
        full_url = self.config['network']['protocol'] + self.config['network']['base_url'] + ":5252" + \
            self.config['network']['get_position_method']

        while True:
            time.sleep(req_interval)
            theta = self.st.get_position()['pos_t']
            try:
                req = requests.post(full_url, data=json.dumps({"theta": theta}))
                if req.status_code == 200:
                    raw_response = req.text
                parsed_response = json.loads(raw_response)
                got_once = True
            except Exception as e:
                self.lg.err("Ошибка подключения к серверу приложения: " + str(e))
            if got_once:
                parsed_response = parsed_response['position']
                self.st.set_position(
                    pos_x=parsed_response['pos_x'],
                    pos_y=parsed_response['pos_y'],
                    accuracy=parsed_response['accuracy']
                )

    def runtime(self):
        got_once = False
        raw_response = "{}"
        parsed_response = {}
        state_interval = float(self.config['general']['state_interval'])
        full_url = self.config['network']['protocol'] + self.config['network']['base_url'] + ":5252" + \
            self.config['network']['get_runtime_method']

        while True:
            time.sleep(state_interval)
            try:
                req = requests.get(full_url)
                if req.status_code == 200:
                    raw_response = req.text
                parsed_response = json.loads(raw_response)
                got_once = True
            except Exception as e:
                self.lg.err("Ошибка подключения к серверу приложения: " + str(e))
            if got_once:
                parsed_response = parsed_response['runtime']
                self.st.set_runtime(
                    state=parsed_response['state'],
                    route=parsed_response['route']
                )
