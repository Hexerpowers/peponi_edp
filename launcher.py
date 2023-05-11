import configparser
import time

from Modules.Common.Logger import Logger
from Modules.Common.Network import Network
from Modules.Handler.MainHandler import MainHandler
from Modules.Store import Store
from Modules.Transport.HttpServer import HttpServer

config = configparser.ConfigParser()
config.read("/home/pi/watchman_endpoint/endpoint.cfg")
# config.read("endpoint.cfg")

LG = Logger(config)
ST = Store(config)
HD = MainHandler(config, ST, LG)
TR = HttpServer(config, ST, LG)
NW = Network(config, ST, LG)

NW.wait_for_connection()

HD.start()
TR.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt as e:
    LG.log('KeyboardInterrupt, остановлено пользователем.')
    LG.__del__()
