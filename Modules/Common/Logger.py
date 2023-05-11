import os
from datetime import datetime

from rich.console import Console


class Logger:
    def __init__(self, config):
        self.config = config
        self.cls = Console()
        self.log_list = ''''''
        if config['general']['log_clear'] == 1:
            self.log_file = open(os.path.dirname(os.path.abspath(__file__)) + '/../../log.txt', 'w+')
        else:
            self.log_file = open(os.path.dirname(os.path.abspath(__file__)) + '/../../log.txt', 'a+')
        self.log_file.write("---------------STARTUP---------------\n")
        self.log_file.close()

    def __del__(self):
        self.cls.print(
            "[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][blue bold]INFO[/][red bold]::[/]Завершение работы.")
        self.log_file = open(os.path.dirname(os.path.abspath(__file__)) + '/../../log.txt', 'a+')
        self.log_file.write('[' + str(datetime.now()) + ']::INFO::Завершение работы.\n')
        self.log_file.write("---------------SHUTDOWN---------------\n")
        self.log_file.close()

    def log(self, msg):
        self.log_file = open(os.path.dirname(os.path.abspath(__file__)) + '/../../log.txt', 'a+')
        self.log_list += '[' + str(datetime.now()) + ']::INFO::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::INFO::' + msg + '\n')
        self.log_file.close()
        self.cls.print("[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][blue bold]INFO[/][red bold]::[/]" + msg)

    def error(self, msg):
        self.log_file = open(os.path.dirname(os.path.abspath(__file__)) + '/../../log.txt', 'a+')
        self.log_list += '[' + str(datetime.now()) + ']::ERROR::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::ERROR::' + msg + '\n')
        self.log_file.close()
        self.cls.print("[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][red bold]ERROR[/][red bold]::[/]" + msg)

    def warn(self, msg):
        self.log_file = open(os.path.dirname(os.path.abspath(__file__)) + '/../../log.txt', 'a+')
        self.log_list += '[' + str(datetime.now()) + ']::WARN::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::WARN::' + msg + '\n')
        self.log_file.close()
        self.cls.print(
            "[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][yellow bold]WARN[/][red bold]::[/]" + msg)

    def init(self, msg):
        self.log_file = open(os.path.dirname(os.path.abspath(__file__)) + '/../../log.txt', 'a+')
        self.log_list += '[' + str(datetime.now()) + ']::INIT::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::INIT::' + msg + '\n')
        self.log_file.close()
        self.cls.print(
            "[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][purple bold]INIT[/][red bold]::[/]" + msg)

    def get_log_list(self):
        return self.log_list
