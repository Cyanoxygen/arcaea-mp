from datetime import datetime
from time import sleep
from arcaea.MultiPlayer import Multiplayer
from arcaea.RedisClient import RedisClient
import json
import threading
from arcaea import config


def curtime():
    return int(datetime.now().timestamp())


class MultiplayerHandler:
    def __init__(self):
        """
        The listener process.
        This listener will repeatly check mp rooms in the list and automatically score them.
        """
        self.mplist = {}
        self.status = 'running'
        self.threadlist = []  # list of thread
        self.mainthread = None
        self.recyclethread = None

    def recycle(self):
        while True:
            for thread in self.threadlist:
                if thread.is_alive() is not True:
                    self.threadlist.pop(thread)
            sleep(5)

    def start(self):
        self.recyclethread = threading.Thread(target=self.recycle)
        self.mainthread = threading.Thread(target=self.listen)
        self.recyclethread.start()
        self.mainthread.start()

    def addmp(self, ident, host, title='Arcaea Multiplayer', members=10):
        self.mplist[str(ident)] = Multiplayer(host, name=title, members=members)

    def listen(self):
        while True:
            '''
            Main loop of the listener.
            '''
            if self.status != 'running':
                break
            for _mp in self.mplist:
                mp = self.mplist[_mp]
                if mp.round_current == 0:
                    continue
                if mp.status == 'stopped' and mp.scored != mp.round_current:
                    print(f'Scoring mproom {mp.id}, name={mp.title}')
                    self.threadlist.append(threading.Thread(target=mp.score()))
                    self.threadlist[len(self.threadlist) - 1].start()
                if curtime() - mp.time[f'round_{mp.round_current}']['start'] >= config.threshold:
                    print(f'Stopping mproom {mp.id}, {mp.title}')
                    mp.stop()

            sleep(5)

