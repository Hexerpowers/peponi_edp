import math
import time
from threading import Thread

from fastapi import FastAPI, Request
import uvicorn
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

        @self.api.post("/api/v1/post/settings")
        async def set_settings(data: Request):
            settings = await data.json()
            self.st.set_runtime('takeoff_speed', settings['takeoff_speed'])
            self.st.set_runtime('ground_speed', settings['ground_speed'])
            self.st.set_runtime('target_alt', settings['target_alt'])
            return {
                "status": "OK"
            }

        @self.api.post("/api/v1/post/move")
        async def post_move(data: Request):
            controls = await data.json()
            self.st.set_move(controls['x'], controls['y'])
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/get/status")
        async def get_logs():
            self.st.set_gui_timestamp(math.floor(time.time()))
            return {
                "status": "OK"
            }

        @self.api.get("/api/v1/get/logs")
        async def get_logs():
            return {
                "status":"OK",
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
                "state": str(self.st.get_power()['state']),
                "voltage": str(self.st.get_power()['voltage']),
                "current": str(self.st.get_power()['current']),
            }

        @self.api.get("/api/v1/get/ready")
        async def get_ready():
            return {
                "ready": str(self.st.get_ready())
            }

        self.lg.log("Принимаю запросы...")
        uvicorn.run(self.api, host="0.0.0.0", port=5052, log_level="critical")
