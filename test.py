import logging
from watcher.boardwatcher2 import BoardWatcher
import asyncio


async def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.DEBUG)

    bw = BoardWatcher()
    threads = await bw.update()
    print(threads)
    print([t.url for t in threads])
    await bw.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())