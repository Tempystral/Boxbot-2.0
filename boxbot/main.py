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


'''watcher = BoardWatcher()
newThreads = watcher.update()
for thread in newThreads:
	print(thread.url)


if __name__ == "__main__":
	logging.basicConfig(
		format='%(asctime)s %(levelname)s:%(message)s',
		level=logging.DEBUG)

	notify2.init("thread watcher")

	bw = BoardWatcher()
	
	cwd = os.path.dirname(os.path.realpath(__file__))

	while True:
		logging.info("checking for new threads...")
		newthreads = bw.update()
		for i in newthreads:
			sub = i.subject + ' ' if i.subject else ''
			com = i.comment.split('\n', 1)[0]
			for _ in range(5):
				try:
					notify2.Notification("/{}/: {}".format(i.board, sub + com),
						"<a href=\"{}\">{}</a>".format(i.url, sub + com),
						cwd + "/clover.png"
					).show()
				except dbus.exceptions.DBusException as e:
					notify2.init("thread_watcher")
				else:
					break
			else:
				raise e
		time.sleep(15*60)'''
