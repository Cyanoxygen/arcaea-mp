from datetime import datetime
from time import sleep
from arcaea.MultiPlayer import Multiplayer
import threading
import config


def curtime():
    return int(datetime.now().timestamp())


class MultiplayerListener:
    def __init__(self, threaded=True):
        """
        The listener process.
        This listener will repeatly check mp rooms in the list and automatically score them.
        """
        self.mplist = {}
        self.status = 'running'
        self.threadlist = []  # list of thread
        self.mainthread = None
        self.recyclethread = None
        self.threaded = threaded

    def recycle(self):
        while True:
            for thread in self.threadlist:
                if thread.is_alive() is not True:
                    self.threadlist.pop(self.threadlist.index(thread))
            sleep(5)

    def start(self):
        if not self.threaded:
            self.mainthread = None
        else:
            self.mainthread = threading.Thread(target=self.listen)
        self.recyclethread = threading.Thread(target=self.recycle)
        self.recyclethread.start()
        self.mainthread.start()

    def addmp(self, ident, host, title='Arcaea Multiplayer', members=10):
        self.mplist[str(ident)] = Multiplayer(ident=ident, host=host, name=title, members=members)

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
                    if mp.round_current != mp.scored:
                        print(f'Stopping mproom {mp.id}, {mp.title}')
                        mp.stop()

            sleep(5)

