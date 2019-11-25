#!/usr/bin/env python3
import time
import os
import logging

from watcher.boardwatcher2 import BoardWatcher
from boxbot import BoxBot

if __name__ == "__main__":
	logging.basicConfig(
		format='%(asctime)s %(levelname)s:%(message)s',
		level=logging.WARN)
	bot = BoxBot()
	bot.run()
