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

NW.wait_for_connection()

HD.start()
TR.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt as e:
    LG.log('KeyboardInterrupt, остановлено пользователем')
