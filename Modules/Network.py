import time

import pythonping


# from netifaces import interfaces, ifaddresses, AF_INET


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

    def ping_inet(self):
        try:
            response_list = pythonping.ping('8.8.8.8', size=10, count=2, timeout=2)
            ping = response_list.rtt_avg_ms
            if ping < 2000:
                self.lg.log("Пинг до Google (наличие сети): "+str(ping)+" ms")
                return True
            else:
                self.lg.err("Ошибка подключения к сети: превышено время ожидания (2000ms).")
                return False
        except Exception as e:
            self.lg.err("Ошибка обнаружения сети: "+str(e))
            return False

    def ping_server(self):
        try:
            response_list = pythonping.ping(self.config['network']['base_url'], size=10, count=2, timeout=2)
            ping = response_list.rtt_avg_ms
            if ping < 2000:
                self.lg.log("Пинг до сервера приложения: "+str(ping)+" ms")
                return True
            else:
                self.lg.err("Ошибка подключения к серверу приложения: превышено время ожидания (2000ms).")
                return False
        except Exception as e:
            self.lg.err("Ошибка обнаружения сервера: "+str(e))

