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

        @self.api.post("/api/v1/post/settings")
        async def set_settings(data: Request):
            settings = await data.json()
            self.st.set_runtime('takeoff_speed', settings['takeoff_speed'])
            self.st.set_runtime('ground_speed', settings['ground_speed'])
            self.st.set_runtime('target_alt', settings['target_alt'])
            self.st.set_runtime('return_alt', settings['return_alt'])
            return {
                "status": "OK"
            }

        @self.api.post("/api/v1/post/move")
        async def post_move(data: Request):
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
        async def get_logs():
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
            return {
                "charge": str(self.st.get_battery_charge())
            }

        @self.api.get("/api/v1/get/power")
        async def get_power():
            return {
                "state": int(self.st.get_power()['state']),
                "voltage": str(self.st.get_power()['voltage']),
                "current": str(self.st.get_power()['current']),
            }

        @self.api.get("/api/v1/get/telemetry")
        async def get_telemetry():
            return {
                "alt": str(self.st.get_telemetry()['alt']),
                "roll": str(self.st.get_telemetry()['roll']),
                "pitch": str(self.st.get_telemetry()['pitch']),
                "yaw": str(self.st.get_telemetry()['yaw']),
            }

        self.lg.log("Принимаю запросы...")
        uvicorn.run(self.api, host="0.0.0.0", port=5052, log_level="critical")

        # uvicorn.run(self.api, host="0.0.0.0", port=5052, log_level="critical")
