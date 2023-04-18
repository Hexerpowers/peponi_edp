class Store:
    def __init__(self):
        self.signals = {
            "takeoff": False,
            "land": False,
            "stop": False,
            "photo": False
        }

        self.move = {
            "x": 0,
            "y": 0,
            "yaw":0,
            "cam_pitch": 0,
            "cam_zoom": 0
        }

        self.runtime = {
            "comm_ok": False,
            "takeoff_speed": 0.5,
            "ground_speed": 0.5,
            "target_alt": 2,
            "return_alt": 2,
            "mode": 0,
            "copter_state": 0
        }

        self.telemetry = {
            "alt": 0,
            "roll": 0,
            "pitch": 0,
            "yaw": 0,
        }

        self.tracking = {
            "gui_timestamp": 0,
            "hank_timestamp": 0,
        }

        self.ping = 2000

        self.battery_charge = 0

        self.power = {
            "state": 0,
            "voltage": 0,
            "current": 0
        }

    def get_telemetry(self):
        return self.telemetry

    def get_signals(self):
        return self.signals

    def get_runtime(self):
        return self.runtime

    def get_move(self):
        return self.move

    def get_ping(self):
        return self.ping

    def get_tracking(self):
        return self.tracking

    def get_battery_charge(self):
        return self.battery_charge

    def get_power(self):
        return self.power

    def set_signal(self, signal, val):
        self.signals[signal] = val

    def set_runtime(self, name, val):
        self.runtime[name] = val

    def set_move(self, move_x, move_y, move_yaw, camera_pitch, camera_zoom):
        self.move = {
            "x": float(move_x) * float(self.runtime['ground_speed']),
            "y": float(move_y) * float(self.runtime['ground_speed']),
            "yaw": int(move_yaw),
            "cam_pitch": int(camera_pitch),
            "cam_zoom": int(camera_zoom),
        }

    def set_gui_timestamp(self, timestamp):
        self.tracking['gui_timestamp'] = timestamp

    def set_ping(self, ping):
        self.ping = ping

    def set_battery_charge(self, level):
        self.battery_charge = level

    def set_power(self, power):
        self.power = power

    def set_copter_state(self, state):
        self.runtime['copter_state'] = state

    def set_telemetry(self, telemetry):
        self.telemetry = telemetry

    def drop_signals(self):
        self.signals = {
            "takeoff": False,
            "land": False,
            "stop": False,
            "photo": False
        }
