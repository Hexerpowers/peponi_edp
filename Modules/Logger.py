from rich.console import Console


class Logger:
    def __init__(self):
        self.cls = Console()

    def log(self, msg):
        self.cls.print("[blue bold]INFO[/][red bold]::[/]" + msg)

    def err(self, msg):
        self.cls.print("[red bold]ERROR[/][red bold]::[/]" + msg)
