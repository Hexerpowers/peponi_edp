class Executor:
    def __init__(self, config, st, lg):
        self.config = config
        self.lg = lg
        self.st = st

    def run(self):
        self.st.set_theta(200)
