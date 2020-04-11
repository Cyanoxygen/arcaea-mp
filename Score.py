import websockets
import asyncio
import brotli
import json
from .Exceptions import QueryFailed


class Score:
    def __init__(self, user):
        self.user = user
        self.name = ''
        self.song_id = ''
        self.ptt = 0.0
        self.difficulty = 0
        self.score = 0
        self.counts = [0, 0, 0, 0]
        self.cleartype = 0,
        self.playtime = 0
        self.rating = 0.0
        self.const = 0.0
        self.raw = {}
        for i in range(1, 3):
            if self.song_id != '':
                break
            try:
                self.update()
            except:
                print(f'Score {self.user} attempt {i} failed.')
                pass
        if self.song_id == '':
            raise QueryFailed

    def update(self):
        """
        Fetch latest score from user.
        Using https://gist.github.com/esterTion/c673a5e2547cd54c202f129babaf601d
        :return: None
        """
        uri = 'wss://arc-src.estertion.win:616'

        async def fetch(obj, user):
            async with websockets.connect(uri, ssl=True) as ws:
                await ws.send(user)
                res = []
                for i in range(0, 3):
                    res.append(await ws.recv())
                await ws.close()
                decoded = json.loads(brotli.decompress(res[2]).decode('utf-8'))
                obj.name = decoded['data']['name']
                obj.ptt = float(decoded['data']['rating']) / 100
                obj.raw = decoded['data']['recent_score'][0]
        loop = asyncio.new_event_loop()
        loop.run_until_complete(fetch(self, self.user))  # Fetch score

        self.song_id = self.raw['song_id']
        self.difficulty = int(self.raw['difficulty'])
        self.score = int(self.raw['score'])
        self.counts = [
            int(self.raw['perfect_count']),
            int(self.raw['shiny_perfect_count']),
            int(self.raw['near_count']),
            int(self.raw['miss_count'])
        ]
        self.cleartype = int(self.raw['clear_type'])
        self.rating = float(self.raw['rating'])
        self.const = float(self.raw['constant'])
        self.playtime = int(self.raw['time_played'])

    def __str__(self):
        return f"{self.name} {self.user} {self.ptt} {self.song_id} {self.score}"

    def __repr__(self):
        return {'username': self.name, 'usercode': self.user, 'ptt': self.ptt, 'song': self.song_id,
                'score': self.score, 'cleartype': self.cleartype, 'const': self.const,
                'rating': self.rating, 'counts': self.counts, 'playtime': self.playtime}

def User_exists(user):
    try:
        user_ = int(user, base=10)
    except:
        return False
    uri = 'wss://arc-src.estertion.win:616'

    async def fetch(usercode):
        async with websockets.connect(uri, ssl=True) as ws:
            await ws.send(usercode)
            res = await ws.recv()
            if res != 'queried':
                return {'status': 'failed'}
            res = await ws.recv()
            res = await ws.recv()
            await ws.close()
            if type(res) == str and 'error' in res:
                return {'status': 'failed'}
            else:
                decoded = json.loads(brotli.decompress(res).decode('utf-8'))
                return {'status': 'ok', 'username': decoded['data']['name'], 'usercode': usercode,
                        'ptt': float(decoded['data']['rating']) / 100}

    return asyncio.new_event_loop().run_until_complete(fetch(str(user)))
