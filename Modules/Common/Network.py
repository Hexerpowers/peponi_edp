import time

from netifaces import interfaces, ifaddresses, AF_INET


class Network:
    def __init__(self, config, st, lg):
        self.config = config
        self.st = st
        self.lg = lg

    def wait_for_connection(self):
        key_0 = str(self.config['network']['common_subnet_0'])
        key_1 = str(self.config['network']['common_subnet_1'])
        self.lg.log("Жду подключение с подсетью " + key_0 + "...")
        self.lg.log("Жду подключение с подсетью " + key_1 + "...")
        local_addr = None
        net_available = False
        while not net_available:
            for ifaceName in interfaces():
                addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
                for addr in addresses:
                    if (key_0 in addr) or (key_1 in addr):
                        local_addr = addr
            if local_addr:
                net_available = True
                self.lg.log("Сетевое подключение [" + str(local_addr) + "] обнаружено.")
            time.sleep(1)
