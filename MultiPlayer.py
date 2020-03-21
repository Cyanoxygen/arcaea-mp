from .RedisClient import RedisClient as Redis
from .Score import Score
from .Songlist import *
from .Exceptions import *
import datetime

index = ['PST', 'PRS', 'FTR']
index_full = ['Past', 'Present', 'Future']


def curtime():
    return int(datetime.datetime.now().timestamp())


class Event:
    def __init__(self, event_type, caption, user, round, reason=''):
        self.event_type = event_type
        self.caption = caption
        self.user = user
        self.time = curtime()
        self.round = round
        self.reason = reason
        self._()

    def __str__(self):
        return f'{datetime.datetime.fromtimestamp(self.time)} type={self.event_type} user={self.user} \
            round= {self.round} {self.caption}, reason {self.reason}'

    def _(self):
        print(self)


class Multiplayer:

    def __init__(self, host, name='Arcaea Multiplayer', members=5, mode='normal'):
        """
        Defines a Multiplayer room.
        :param host: Creator of the room, Arcaea ID
        :param name: Title of the room.
        :param members: Max members of the room.
        :param mode: 'normal' Normal room 'casual' Casual play 'vs' 1-1 VS Mode
        """
        self.id = int(Redis.incr('lastid')) + 1  # Multiplayer room ID
        self.title = name  # Room Title
        self.mode = mode  # Playmode, 'normal' or 'casual'
        self.max_members = members  # Member limit
        self.round_current = 0  # Current round
        self.rounds = [{}]  # Total rounds
        self.host = host  # Host of the room, Arcaea ID
        self.count = 1  # Total members of the room, including the host
        self.members = [host]  # Members of the room
        self.scores = {}  # Scores of each round
        self.ranks = []  # Ranking of each round
        self.status = 'idle'  # Status of the room ('idle', 'playing', 'scoring', 'closed', 'stopped'
        # 'full')
        self.time = {}      # Start and end time of each round
        self.scored = 0     # Flags the scoring status for preventing endless loop
        self.events = []  # Event of this room (joining, leaving, etc)
        self.song_current = ''  # Currently playing song
        self.events.append(Event('created', f'Room {self.id} created', '', self.round_current))
        self.rounds.append({})
        Redis.hset(f'arcaeamp:{self.id}', 'host', self.host)
        Redis.hset(f'arcaeamp:{self.id}', 'title', self.title)

    def add_member(self, userid, callback=None):
        if self.count == self.max_members:
            raise RoomIsFull
        self.members.append(userid)
        self.count = len(self.members) + 1

    def rm_member(self, userid, reason='', callback=None):
        if userid not in self.members:
            raise KeyError(f'{userid} is not found in this mp room.')
        self.members.pop(self.members.index(userid))
        self.count -= 1
        self.events.append(Event('remove', f'user {userid} has been removed', userid, self.round_current, reason))
        if self.members.__len__() == 0:
            self.status = 'closed'
        if callback:
            callback(reason)

    def close(self):
        for member in self.members:
            if member == self.host:
                pass
            self.rm_member(member, reason='closing')
        self.rm_member(self.host)

    def set_song(self, songid: str, difficulty: str):
        if songid not in songs_by_id:
            raise SongNotFoundError(songid)
        if difficulty.upper() not in index:
            raise InvalidDifficulty

        self.rounds[self.round_current + 1]['id'] = songid
        self.rounds[self.round_current + 1]['difficulty'] = index.index(difficulty.upper())
        self.song_current = self.rounds[self.round_current + 1]['id']

    def update_score(self):
        self.status = 'scoring'
        self.scores[f'round_{self.round_current}'] = []
        for user in self.members:
            self.scores[f'round_{self.round_current}'].append(Score(user))

        self.status = 'idle'

    def nextround(self):
        self.status = 'playing'
        self.round_current += 1
        self.events.append(Event('start', f'Round {self.round_current} started', '', self.round_current))
        self.time[f'round_{self.round_current}'] = {'start': curtime()}  # Record current time
        Redis.hincrby(f'arcaeamp:{self.id}', 'rounds')

    def stop(self):
        self.status = 'stopped'
        self.time[f'round_{self.round_current}']['stop'] = curtime()
        self.events.append(Event('stop', f'Round {self.round_current} stopped', '', self.round_current))

    def score(self, callback=None):
        self.update_score()
        for score in self.scores[f'round_{self.round_current}']:
            if score.song_id != self.rounds[self.round_current]['id']:
                self.rm_member(score.user, reason='invsongkick', callback=callback)
            if score.difficulty != self.rounds[self.round_current]['difficulty']:
                self.rm_member(score.user, reason='invdiffkick', callback=callback)

        self.scores[f'round_{self.round_current}'].sort(key=lambda x: x.score, reverse=True)
        Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}', 'len', len(self.scores))
        for score in self.scores[f'round_{self.round_current}']:
            i = self.scores[f'round_{self.round_current}'].index(score) + 1
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'userid',score.user)
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'username', score.name)
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'score', score.score)
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'rating', score.rating)
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'pure', score.counts[0] + score.counts[1])
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'far', score.counts[2])
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'miss', score.counts[3])
            Redis.hset(f'arcaeamp:{self.id}:round_{self.round_current}:score{i}', f'time', score.playtime)
        self.rounds.append({})  # Prepare for the next round
        self.status = 'idle' if self.count < self.max_members else 'full'  # Change status
        self.scored = self.round_current
