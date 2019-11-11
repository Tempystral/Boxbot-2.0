import re, os, logging, aiohttp

from watcher import fourchanaio as fourchan

class BoardWatcher:
	def __init__(self, patternFile=".config/patterns.txt"):
		self._last_modified_time = 0
		self._patternFile = patternFile
		self._chan = fourchan.Chan()

		self._patterns = {}
		self._exclude_patterns = {}
		self._boards = set()
		self._tracked_threads = {}
		try:
			self.load_patterns(self._patternFile)
		except FileNotFoundError:
			logging.warning("Patterns file not found")

	async def update(self):
		'''Refresh the internal database and return a list of new threads'''
		t = os.path.getmtime(self._patternFile)
		if t > self._last_modified_time:
			logging.info("Updating pattern list")
			self.load_patterns(self._patternFile)
			self._last_modified_time = t
			logging.debug(self._patterns)
		newThreads = []
		# Clean threadlist, then update boards
		await self.cleanup_untracked_boards()
		for board in self._boards:
			newMatchedThreads = await self.update_board(board)
			newThreads.extend(newMatchedThreads)
		return newThreads

	async def update_board(self, board):
		logging.info(f"checking for new threads on {board}")

		# Get new threads from 4chan
		liveThreads = await self._retrieve_threads(board)
		self.cleanup_board(board, liveThreads)
		
		threadNos = [t.no for t in liveThreads]
		newThreads = []
		filtered = [i for i in liveThreads 
								if 			any(map(lambda x: x.search(i.comment) or x.search(i.subject), self._patterns.get(board, [])))
								and not any(map(lambda x: x.search(i.comment) or x.search(i.subject), self._exclude_patterns.get(board, [])))]
		
		# Add new threads only if they are not being tracked
		for thread in filtered:
			if thread.no not in self._tracked_threads[board]:
				newThreads.append(thread)
				logging.info(f"Started tracking {thread.url}")
				self._tracked_threads[board][thread.no] = thread
		return newThreads

	def cleanup_board(self, board, threads):
		'''Remove dead threads in tracked boards'''
		threadNos = [t.no for t in threads]
		for no in list(self._tracked_threads.setdefault(board, {})):
			if not no in threadNos:
				t = self._tracked_threads[board].pop(no)
				logging.info(f"Stopped tracking {t.url}")
	
	async def cleanup_untracked_boards(self):
		'''Remove threads belonging to untracked boards'''
		untrackedBoards = [b for b in self._tracked_threads if b not in self._boards]
		for board in untrackedBoards:
			for no in self._tracked_threads[board]:
				thread = self._tracked_threads[board][no]
				logging.info(f"Stopped tracking {thread.url}")
			self._tracked_threads.pop(board, None)
			self._patterns.pop(board, None)
			self._exclude_patterns.pop(board, None)

	def load_patterns(self, filename):
		self._boards = set()	# Clear the bag of boards
		with open(filename) as f:
			for count, line in enumerate(f):
				# Ignore commented or empty lines
				if line.strip()[0] == '#' or len(line.strip()) == 0:
					continue
				# Match options using a regex
				match = re.match(r'(.+)\|(.*)\|(.+)', line)				#match = re.match(r'\/(.*)\/(\w*);(.*)', line)
				try: # Parse arguments
					flags, exclude = self.parse_args(match.group(2))		# Tempystral - I don't particularly love multiple returns of unrelated types but it LOOKS clean....
					# Get a list of patterns with regex options
					patterns = self.parse_patterns(match.group(1), flags)
				except re.error as e:
					logging.warning(f"couldn't compile \"{line.rstrip()}\" on line {count+1}:\n{e}")
				else:
					boards = self.parse_boards(match.group(3))
					if exclude:
						for board in boards:
							self._boards.add(board)
							for p in patterns:
								self._exclude_patterns.setdefault(board, []).append(p)
					else:
						for board in boards:
							self._boards.add(board)
							for p in patterns:
								self._patterns.setdefault(board, []).append(p)

	#==============================#
	#				Getters/Setters				 #
	#==============================#

	def setPatternFile(self, filepath):
		self._patternFile = filepath
		if (not os.path.exists(filepath)):
			logging.warning(f"Pattern file does not exist at path {filepath}.")
	
	def addNewPattern(self, pattern):
		'''Add pattern to the patternfile and return success'''
		match = re.match(r'(.+)\|(.*)\|(.+)', pattern)
		if match:
			with open(self._patternFile, "a") as f:
				f.write(f"\n{pattern}")
				return True
		else:
			return False
	
	def getPatterns(self):
		'''Returns a list of regex patterns as strings'''
		return self._patterns
	
	def getExcludePatterns(self):
		'''Returns a list of excluded regex patterns as strings'''
		return self._exclude_patterns
		
	def getBoards(self):
		return self._boards

	def getTrackedThreads(self):
		threads = []
		for board in self._tracked_threads:
			for threadNo in self._tracked_threads[board]:
				threads.append((self._tracked_threads[board][threadNo]))
		return threads

	def setTrackedThreads(self, newDict = {}):
		self._tracked_threads = newDict
	
	def printTrackedThreads(self):
		for board in self._boards:
			for thread in self._tracked_threads[board]:
				print(self._tracked_threads[board][thread].url)
	
	

	#==============================#
	#				 Private methods			 #
	#==============================#

	async def _retrieve_threads(self, board):
		'''Retrieve threads from a specified 4chan board'''
		try:	# Get threads from 4chan
			threads = await self._chan.catalog(board)
			return threads
		except aiohttp.ClientError:
			logging.warning("Failed to update threads due to a network error")
			return []

	def parse_patterns(self, argString, flags):
		'''Parse comma-separated arguments into a list and return regex patterns'''
		patterns = [x.strip() for x in argString.split(",") if len(x.strip()) > 0]
		return [re.compile(x, flags) for x in patterns] # Compile patterns

	def parse_args(self, argString):
		'''Parse a string of arguments and return the respective flags'''
		# Split arguments into an array, strip whitespace, and remove null values all at once!
		# List comprehension is wonderful!
		args = [x.strip() for x in argString.split(",") if len(x.strip()) > 0]
		regex_flags = 0
		exclude = False
		for a in args:
			if a == "i":
				regex_flags |= re.IGNORECASE
			elif a == "e":
				exclude = True
		return regex_flags, exclude

	def parse_boards(self, argString):
		'''Parse boards and add to an array'''
		return [x.strip() for x in argString.split(",") if len(x.strip()) > 0]
	
	async def close(self) -> type(None):
		await self._chan.close()