from threading import Thread


class Handler:
    def __init__(self, config, st, lg):
        self.config = config
        self.st = st
        self.lg = lg
        self.main = Thread(target=self.main, daemon=True, args=())

    def start(self):
        self.main.start()

    def main(self):
        pass
