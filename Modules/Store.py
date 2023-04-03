class Store:
    def __init__(self):
        self.signals = {
            "takeoff": False,
            "landing": False,
            "manual": False,
        }

        self.move = {
            "x": 0,
            "y": 0,
        }

        self.runtime = {
            "comm_ok": False,
            "takeoff_speed": 0.5,
            "ground_speed": 0.5,
            "target_alt": 2,
            "mode": 0
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

        self.ready = 0

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

    def get_ready(self):
        return self.ready

    def set_signal(self, signal, val):
        self.signals[signal] = val

    def set_runtime(self, name, val):
        self.runtime[name] = val

    def set_move(self, move):
        self.move = {
            "x": move[0] * self.runtime['ground_speed'],
            "y": move[1] * self.runtime['ground_speed']
        }

    def set_gui_timestamp(self, timestamp):
        self.tracking['gui_timestamp'] = timestamp

    def set_ping(self, ping):
        self.ping = ping

    def set_battery_charge(self, level):
        self.battery_charge = level

    def set_power(self, power):
        self.power = power

    def set_ready(self, state):
        self.ready = state
