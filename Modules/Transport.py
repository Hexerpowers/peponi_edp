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
        self.telemetry_loop = Thread(target=self.telemetry, daemon=True, args=())

    def start(self):
        self.position_loop.start()
        self.telemetry_loop.start()

    def position(self):
        got_once = False
        raw_response = "{}"
        parsed_response = {}
        req_interval = float(self.config['general']['req_interval'])
        full_url = self.config['network']['protocol'] + self.config['network']['base_url'] + ":8000" + \
            self.config['network']['get_method']

        while True:
            time.sleep(req_interval)
            try:
                req = requests.get(full_url)
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
                    pos_a=parsed_response['pos_a'],
                    accuracy=parsed_response['accuracy']
                )

    def telemetry(self):
        req_interval = float(self.config['general']['req_interval'])
        full_url = self.config['network']['protocol'] + self.config['network']['base_url'] + ":8000" + \
            self.config['network']['post_method']

        while True:
            time.sleep(req_interval)
            telemetry = self.st.get_telemetry()
            try:
                req = requests.post(full_url, data=json.dumps(telemetry))
                if req.status_code != 200:
                    self.lg.err("Ошибка подключения к серверу приложения: status_code=" + str(req.status_code))
            except Exception as e:
                self.lg.err("Ошибка получения информации от сервера: " + str(e))
