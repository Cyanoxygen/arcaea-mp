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

    def __init__(self, ident, host, name='Arcaea Multiplayer', members=5, mode='normal'):
        """
        Defines a Multiplayer room.
        :param host: Creator of the room, Arcaea ID
        :param name: Title of the room.
        :param members: Max members of the room.
        :param mode: 'normal' Normal room 'casual' Casual play 'vs' 1-1 VS Mode

        You may need to register some event calls in order to know what happened during play.
        """
        self.id = ident  # Multiplayer room ID
        self.title = name  # Room Title
        self.mode = mode  # Playmode, 'normal' or 'casual'
        self.max_members = members  # Member limit
        self.round_current = 0  # Current round
        self.rounds = [{}]  # Total rounds
        self.host = host  # Host of the room, Arcaea ID
        self.creator = host     # Creator of the room
        self.count = 1  # Total members of the room, including the host
        self.members = [host]  # Members of the room
        self.scores = {}  # Scores of each round
        self.ranks = [['dummy'], ]  # Ranking of each round
        self.status = 'idle'  # Status of the room ('idle', 'playing', 'scoring', 'closed', 'stopped'
        # 'full')
        self.time = {}      # Start and end time of each round
        self.scored = 0     # Flags the scoring status for preventing endless loop
        self.events = []  # Event of this room (joining, leaving, etc)
        self.song_current = ''  # Currently playing song
        self.diff_current = ''  # Current beatmap level
        self.ignorediff = False
        self.events.append(Event('created', f'Room {self.id} created', '', self.round_current))
        self.rounds.append({})
        self.calls = {      # This is a event-based lib (probably)

        }

    def regcall(self, calltype, call):
        if callable(call):
            if calltype in ['onCreate', 'onRemove', 'onHostChange', 'onClose', 'onStart', 'onStop', 'onScoreComplete']:
                self.calls[calltype] = call

            else:
                raise Exception('Invalid call type.')

        else:
            raise Exception("It's not callable.")

    def cur_song(self):
        if self.round_current == 0:
            if len(self.rounds[-1]) == 2:
                return self.rounds[-1]['id'], self.rounds[-1]['difficulty']
            else:
                return ('dummy', 'prs')
        else:
            if len(self.rounds[-1]) == 0:
                return self.rounds[-2]['id'], self.rounds[-2]['difficulty']
            return self.rounds[-1]['id'], self.rounds[-1]['difficulty']

    def add_member(self, userid):
        if self.count == self.max_members:
            raise RoomIsFull
        self.members.append(userid)
        self.count = len(self.members) + 1

    def rm_member(self, userid, reason=''):
        if userid not in self.members:
            raise KeyError(f'{userid} is not found in this mp room.')
        self.members.pop(self.members.index(userid))
        self.count -= 1
        self.events.append(Event('remove', f'user {userid} has been removed', userid, self.round_current, reason))
        if 'onRemove' in self.calls.keys():
            call = self.calls['onRemove']
            call(self, userid, reason)
        if self.members.__len__() == 0:
            self.status = 'closed'
            self.close()
            return
        if userid == self.host:
            self.change_host(self.members[0])

    def change_host(self, member):
        if member not in self.members:
            raise Exception('Member not found')
        oldhost = self.host
        self.host = member
        self.events.append(Event('hostchange', f'Host of {self.id} was changed from {oldhost} to {self.host}',
                                 member, self.round_current))
        if 'onHostChange' in self.calls.keys():
            call = self.calls['onHostChange']
            call(self, oldhost, member)

    def close(self):
        for member in self.members:
            if member == self.host:
                pass
            self.rm_member(member, reason='closing')
        if 'onClose' in self.calls.keys():
            call = self.calls['onClose']
            call(self)

    def set_song(self, songid: str, difficulty: str):
        if songid not in songs_by_id:
            raise SongNotFoundError(songid)
        if difficulty.upper() not in index:
            raise InvalidDifficulty

        self.rounds[self.round_current + 1]['id'] = songid
        self.rounds[self.round_current + 1]['difficulty'] = index.index(difficulty.upper())
        self.song_current = self.rounds[self.round_current + 1]['id']
        self.diff_current = self.rounds[self.round_current + 1]['difficulty']

    def update_score(self):
        self.status = 'scoring'
        self.scores[f'round_{self.round_current}'] = []
        for user in self.members:
            self.scores[f'round_{self.round_current}'].append(Score(user))

        self.status = 'idle'

    def nextround(self):
        if 'id' not in self.rounds[self.round_current + 1].keys():
            self.rounds[self.round_current + 1]['id'] = self.rounds[self.round_current]['id']
            self.rounds[self.round_current + 1]['difficulty'] = self.rounds[self.round_current]['difficulty']
            # Continue as current song and diff

        self.status = 'playing'
        self.round_current += 1
        self.events.append(Event('start', f'Round {self.round_current} started', '', self.round_current))
        self.time[f'round_{self.round_current}'] = {'start': curtime()}  # Record current time

    def stop(self):
        self.status = 'stopped'
        self.time[f'round_{self.round_current}']['stop'] = curtime()
        self.events.append(Event('stop', f'Round {self.round_current} stopped', '', self.round_current))
        if 'onStop' in self.calls.keys():
            call = self.calls['onStop']
            call(self)

    def score(self):
        try:
            self.update_score()
        except QueryFailed as e:
            if 'onException' in self.calls.keys():
                call = self.calls['onException']
                call(self.id, e)
        scores = self.scores[f'round_{self.round_current}']
        for score in scores:
            if score.song_id != self.rounds[self.round_current]['id']:
                self.rm_member(score.user, reason='invsongkick')
                self.scores[f'round_{self.round_current}'].pop(scores.index(score))
            if score.difficulty != self.rounds[self.round_current]['difficulty']:
                if self.ignorediff:
                    pass
                else:
                    self.rm_member(score.user, reason='invdiffkick')
                    self.scores[f'round_{self.round_current}'].pop(scores.index(score))
        if self.status == 'closed':
            return

        self.scores[f'round_{self.round_current}'].sort(key=lambda x: (x.score if not self.ignorediff else x.rating), reverse=True)
        self.ranks.append([])
        for score in self.scores[f'round_{self.round_current}']:
            self.ranks[self.round_current].append(score.user)

        self.rounds.append({})  # Prepare for the next round
        self.status = 'idle' if self.count < self.max_members else 'full'  # Change status
        self.scored = self.round_current
        if 'onScoreComplete' in self.calls.keys():
            call = self.calls['onScoreComplete']
            call(self)

    def __repr__(self):
        dict = {'id': self.id, 'title': self.title, 'creator': self.creator, 'host':self.host, 'rounds': [], 'scores': [], 'ranks': self.ranks}
        for r in self.rounds:
            dict['rounds'].append(r)
        for s in self.scores.keys():
            l = []
            for c in self.scores[s]:
                l.append(c.__repr__())
            dict['scores'].append(l)
        return str(dict)