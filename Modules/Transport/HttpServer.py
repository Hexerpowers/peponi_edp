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



        # @self.api.post("/api/v1/get/position_n_theta")
        # async def get_position_set_theta(data: Request):
        #     theta = await data.json()
        #     self.st.set_theta(theta['theta'])
        #     self.st.set_robot_timestamp(math.floor(time.time()))
        #     return {
        #         "position": self.st.get_position(0)
        #     }

        self.lg.log("Принимаю запросы...")
        uvicorn.run(self.api, host="0.0.0.0", port=5052,)
        # uvicorn.run(self.api, host="0.0.0.0", port=5052, log_level="critical")
