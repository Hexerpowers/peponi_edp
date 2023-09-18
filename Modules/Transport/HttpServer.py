import math
import time
from threading import Thread

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


class HttpServer:
    def __init__(self, config, st, lg):
        self.config = config
        self.st = st
        self.lg = lg

        self.api = FastAPI()
        origins = ["*"]
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.server_loop = Thread(target=self.serve, daemon=True, args=())

    def start(self):
        self.server_loop.start()

    def serve(self):
        @self.api.get("/api/v1/trig/stop")
        async def trig_stop():
            self.st.set_signal("stop", True)
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/trig/takeoff")
        async def trig_takeoff():
            self.st.set_signal("takeoff", True)
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/trig/land")
        async def trig_land():
            self.st.set_signal("land", True)
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/trig/photo")
        async def trig_photo():
            self.st.set_signal("photo", True)
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/trig/mode")
        async def trig_mode():
            self.st.set_signal("main_cam_mode", True)
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/trig/reboot")
        async def trig_reboot():
            self.st.set_reboot_signal()
            return {
                "status": "OK"
            }

        @self.api.post("/api/v1/post/mode")
        async def set_manual_mode(data: Request):
            data = await data.json()
            self.st.set_manual_mode(data['mode'])
            return {
                "status": "OK"
            }

        @self.api.post("/api/v1/post/settings")
        async def set_settings(data: Request):
            settings = await data.json()
            self.st.set_runtime('ground_speed', settings['ground_speed'])
            self.st.set_runtime('target_alt', settings['target_alt'])
            self.st.set_runtime('pir_cam_mode', settings['pir_mode'])
            return {
                "status": "OK"
            }

        @self.api.post("/api/v1/post/dev_settings")
        async def set_dev_settings(data: Request):
            settings = await data.json()
            self.st.set_runtime('takeoff_speed', settings['takeoff_speed'])
            self.st.set_runtime('power_onboard', 1 if settings['power_onboard'] == 'true' else 0)
            self.st.set_gps_mode(1 if settings['mode'] == 'true' else 0)
            return {
                "status": "OK"
            }

        @self.api.post("/api/v1/post/move")
        async def set_move(data: Request):
            controls = await data.json()
            self.st.set_move(
                controls['x'],
                controls['y'],
                controls['yaw'],
                controls['cam_pitch'],
                controls['cam_zoom']
            )
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/get/status")
        async def get_status(data: Request):
            self.st.set_controller_address(data.client.host)
            self.st.set_gui_timestamp(math.floor(time.time()))
            return {
                "status": "OK",
                "copter_state": int(self.st.get_runtime()['copter_state']),
            }

        @self.api.get("/api/v1/get/logs")
        async def get_logs():
            return {
                "status": "OK",
                "log_list": str(self.lg.get_log_list())
            }

        @self.api.get("/api/v1/get/ping")
        async def get_ping():
            return {
                "ping": str(self.st.get_ping())
            }

        @self.api.get("/api/v1/get/charge")
        async def get_charge():
            if int(self.st.config['general']['use_power_telemetry']) == 1:
                charge = str(self.st.get_battery_charge())
            else:
                charge = "99"
            return {
                "charge": charge
            }

        @self.api.get("/api/v1/get/power")
        async def get_power():
            if int(self.st.config['general']['use_power_telemetry']) == 1:
                state = int(self.st.get_power()['state'])
                voltage = str(self.st.get_power()['voltage'])
            else:
                state = 2
                voltage = 48
            return {
                "state": state,
                "voltage": voltage,
                "current_0": str(self.st.get_power()['current_0']),
                "current_1": str(self.st.get_power()['current_1']),
            }

        @self.api.get("/api/v1/get/telemetry")
        async def get_telemetry():
            return {
                "alt": str(self.st.get_telemetry()['alt']),
                "roll": str(self.st.get_telemetry()['roll']),
                "pitch": str(self.st.get_telemetry()['pitch']),
                "yaw": str(self.st.get_telemetry()['yaw']),
                "t_yaw": str(self.st.get_telemetry()['t_yaw'])
            }

        @self.api.get("/api/v1/get/debug")
        async def get_debug():
            return {
                "takeoff": str(self.st.get_signals()['takeoff']),
                "land": str(self.st.get_signals()['land']),
                "stop": str(self.st.get_signals()['stop']),
                "photo": str(self.st.get_signals()['photo']),
                "main_cam_mode": str(self.st.get_signals()['main_cam_mode']),

                "x": str(self.st.get_move()['x']),
                "y": str(self.st.get_move()['y']),
                "yaw": str(self.st.get_move()['yaw']),
                "cam_pitch": str(self.st.get_move()['cam_pitch']),
                "cam_zom": str(self.st.get_move()['cam_zoom']),

                "comm_ok": str(self.st.get_runtime()['comm_ok']),
                "takeoff_speed": str(self.st.get_runtime()['takeoff_speed']),
                "ground_speed": str(self.st.get_runtime()['ground_speed']),
                "target_alt": str(self.st.get_runtime()['target_alt']),
                "copter_state": str(self.st.get_runtime()['copter_state']),
                "pir_cam_mode": str(self.st.get_runtime()['pir_cam_mode']),
                "power_onboard": str(self.st.get_runtime()['power_onboard']),


                "alt": str(self.st.get_telemetry()['alt']),
                "roll": str(self.st.get_telemetry()['roll']),
                "pitch": str(self.st.get_telemetry()['pitch']),
                "tel_yaw": str(self.st.get_telemetry()['yaw']),
                "t_yaw": str(self.st.get_telemetry()['t_yaw']),
                "gps_sat": str(self.st.get_telemetry()['gps_sat']),
                "actual_mode": str(self.st.get_telemetry()['actual_mode']),

                "state": str(self.st.get_power()['state']),
                "voltage": str(self.st.get_power()['voltage']),
                "current_0": str(self.st.get_power()['current_0']),
                "current_1": str(self.st.get_power()['current_1']),
                "charge": str(self.st.get_power()['charge'])
            }

        self.lg.init("Инициализация завершена.")
        if int(self.st.config['general']['show_errors']) == 1:
            uvicorn.run(self.api, host="0.0.0.0", port=5052)
        else:
            uvicorn.run(self.api, host="0.0.0.0", port=5052, log_level="critical")
