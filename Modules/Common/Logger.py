from datetime import datetime

from rich.console import Console


class Logger:
    def __init__(self, config):
        self.cls = Console()
        self.log_list = ''''''
        if config['general']['log'] == 'clear':
            self.log_file = open('log.txt', 'w+')
        else:
            self.log_file = open('log.txt', 'a+')
        self.log_file.write("---------------STARTUP---------------\n")

    def __del__(self):
        self.cls.print(
            "[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][blue bold]INFO[/][red bold]::[/]Завершаю работу")
        self.log_file.write('[' + str(datetime.now()) + ']::INFO::Завершаю работу\n')
        self.log_file.write("---------------SHUTDOWN---------------\n")
        self.log_file.close()

    def log(self, msg):
        self.log_list += '[' + str(datetime.now()) + ']::INFO::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::INFO::' + msg + '\n')
        self.cls.print("[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][blue bold]INFO[/][red bold]::[/]" + msg)

    def error(self, msg):
        self.log_list += '[' + str(datetime.now()) + ']::ERROR::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::ERROR::' + msg + '\n')
        self.cls.print("[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][red bold]ERROR[/][red bold]::[/]" + msg)

    def warn(self, msg):
        self.log_list += '[' + str(datetime.now()) + ']::WARN::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::WARN::' + msg + '\n')
        self.cls.print(
            "[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][yellow bold]WARN[/][red bold]::[/]" + msg)

    def init(self, msg):
        self.log_list += '[' + str(datetime.now()) + ']::INIT::' + msg + '\n'
        self.log_file.write('[' + str(datetime.now()) + ']::INIT::' + msg + '\n')
        self.cls.print(
            "[gray]\[" + str(datetime.now()) + "][/][red bold]::[/][purple bold]INIT[/][red bold]::[/]" + msg)

    def get_log_list(self):
        return self.log_list
