import websockets
import asyncio
import brotli
import json


class Score:
    def __init__(self, user):
        self.user = user
        self.name = ''
        self.song_id = ''
        self.difficulty = 0
        self.score = 0
        self.counts = [0, 0, 0, 0]
        self.cleartype = 0,
        self.playtime = 0
        self.rating = 0.0
        self.const = 0.0
        self.raw = {}
        self.update()

    def update(self):
        """
        Fetch latest score from user.
        Using https://gist.github.com/esterTion/c673a5e2547cd54c202f129babaf601d
        :return: None
        """
        uri = 'wss://arc-src.estertion.win:616'

        async def fetch(self, user):
            async with websockets.connect(uri, ssl=True) as ws:
                await ws.send(user)
                res = []
                for i in range(0, 3):
                    res.append(await ws.recv())

                decoded = json.loads(brotli.decompress(res[2]).decode('utf-8'))
                self.name = decoded['data']['name']
                self.raw = decoded['data']['recent_score'][0]
        loop = asyncio.new_event_loop()
        loop.run_until_complete(fetch(self,self.user))  # Fetch score

        self.song_id = self.raw['song_id']
        self.difficulty = int(self.raw['difficulty'])
        self.score = int(self.raw['score'])
        self.counts = [
            int(self.raw['shiny_perfect_count']),
            int(self.raw['perfect_count']),
            int(self.raw['near_count']),
            int(self.raw['miss_count'])
        ]
        self.cleartype = int(self.raw['clear_type'])
        self.rating = float(self.raw['rating'])
        self.const = float(self.raw['constant'])
        self.playtime = int(self.raw['time_played'])

    def __repr__(self):
        return f"{self.name} {self.song_id} {self.score}"


def user_exists(user):
    try:
        user = int(user)
    except:
        return False
    uri = 'wss://arc-src.estertion.win:616'

    async def fetch(usercode):
        async with websockets.connect(uri, ssl=True) as ws:
            await ws.send(usercode)
            res = await ws.recv()
            if res == 'queried':
                return True
            else:
                return False

    return asyncio.new_event_loop().run_until_complete(fetch(user))
