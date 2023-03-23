class Store:
    def __init__(self):
        self.position = {
            'pos_x': 0,
            'pos_y': 0,
            'pos_a': 0,
            'accuracy': 0,
        }

        self.telemetry = {
            "charge_level": 11,
            "signal_strength": 112323,
        }

    def __str__(self):
        return "Position: " + str(self.position) + "\nTelemetry: " + str(self.telemetry)

    def set_position(self, pos_x, pos_y, pos_a, accuracy):
        self.position['pos_x'] = int(pos_x)
        self.position['pos_y'] = int(pos_y)
        self.position['accuracy'] = int(accuracy)
        self.position['pos_a'] = int(pos_a)

    def set_angle(self, pos_a):
        self.position['pos_a'] = int(pos_a)

    def set_accuracy(self, accuracy):
        self.position['accuracy'] = int(accuracy)

    def get_position(self):
        return self.position

    def set_telemetry(self, charge_level, signal_strength):
        self.telemetry['charge_level'] = int(charge_level)
        self.telemetry['signal_strength'] = int(signal_strength)

    def get_telemetry(self): return self.telemetry
