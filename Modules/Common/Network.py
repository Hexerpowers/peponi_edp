import time
from netifaces import interfaces, ifaddresses, AF_INET


class Network:
    def __init__(self, config, st, lg):
        self.config = config
        self.st = st
        self.lg = lg

    def wait_for_connection(self):
        key = str(self.config['network']['common_subnet'])
        self.lg.log("Жду подключение с подсетью " + key + "...")
        local_addr = None
        net_available = False
        while not net_available:
            for ifaceName in interfaces():
                addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
                for addr in addresses:
                    if key in addr:
                        local_addr = addr
            if local_addr:
                net_available = True
                self.lg.log("Сетевое подключение обнаружено.")
            time.sleep(1)
