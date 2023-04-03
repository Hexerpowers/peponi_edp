import configparser
import time

from Modules.Handler.MainHandler import MainHandler
from Modules.Common.Logger import Logger
from Modules.Store import Store
from Modules.Transport.HttpServer import HttpServer
from Modules.Common.Network import Network

config = configparser.ConfigParser()
config.read("endpoint.cfg")

LG = Logger(config)
ST = Store()
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
    LG.log('KeyboardInterrupt, остановлено пользователем')
