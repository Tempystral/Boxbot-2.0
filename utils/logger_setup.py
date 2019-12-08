import logging
import sys

class MinLevelFilter(logging.Filter):
    def __init__(self, minLevel):
        self.minLevel = minLevel

    def filter(self, record):
        return (record.levelno >= self.minLevel)

class LoggerSetup:
    def __init__(self):
        self.logger = logging.getLogger('discord')
        self.logformatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
        self.handler_file = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
        #self.handler_debug = logging.FileHandler(filename='discord.debug.log', encoding='utf-8', mode='a')
        self.handler_shell = logging.StreamHandler(stream=sys.stdout)
        self.__setup()

    def __setup(self):
        # Base logger sees all levels
        self.logger.setLevel(logging.INFO)
        # Special logs will see all logging levels
        #self.handler_debug.setFormatter(self.logformatter)
        #self.handler_debug.addFilter(MinLevelFilter(logging.DEBUG))
        # File writer will see all logging levels
        self.handler_file.setFormatter(self.logformatter)
        self.handler_file.addFilter(MinLevelFilter(logging.INFO))
        # Shell will only see warnings and above
        self.handler_shell.setFormatter(self.logformatter)
        self.handler_file.addFilter(MinLevelFilter(logging.WARNING))

        #self.logger.addHandler(self.handler_debug)
        self.logger.addHandler(self.handler_file)
        self.logger.addHandler(self.handler_shell)

logger = LoggerSetup().logger