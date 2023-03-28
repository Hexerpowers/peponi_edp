class Store:
    def __init__(self):
        self.position = {
            'pos_x': 0,
            'pos_y': 0,
            'pos_t': 0,
            'accuracy': 0,
        }

        self.runtime = {
            "state": False,
            "route": {}
        }

    def __str__(self):
        return "Position: " + str(self.position)

    def set_position(self, pos_x, pos_y, accuracy):
        self.position['pos_x'] = int(pos_x)
        self.position['pos_y'] = int(pos_y)
        self.position['accuracy'] = int(accuracy)

    def set_theta(self, pos_t):
        self.position['pos_t'] = int(pos_t)

    def set_runtime(self, state, route):
        self.runtime['state'] = bool(state)
        self.runtime['route'] = route

    def get_position(self): return self.position

    def get_state(self):
        return self.runtime['state']

    def get_route(self):
        if len(self.runtime['route']) == 0:
            return False
        else:
            return self.runtime['route']
