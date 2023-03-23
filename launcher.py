import configparser
import time

from Modules.Handler import Handler
from Modules.Logger import Logger
from Modules.Store import Store
from Modules.Transport import Transport
from Modules.Network import Network

config = configparser.ConfigParser()
config.read("endpoint.cfg")

LG = Logger()
ST = Store()
HD = Handler(config, ST, LG)
TR = Transport(config, ST, LG)
NW = Network(config, ST, LG)

# NW.wait_for_connection()
NW.ping_inet()
boot_lock = NW.ping_server()

if boot_lock or config['general']['mode'] == 'test':
    HD.start()
    TR.start()

    while True:
        time.sleep(1)
