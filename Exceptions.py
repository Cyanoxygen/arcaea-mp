class UserNotFoundError(BaseException):
    def __init__(self, usercode):
        self.usercode = usercode

    def __str__(self):
        return f'The usercode {self.usercode} is not found in Arcaea server.'


class SongNotFoundError(BaseException):
    def __init__(self, song):
        self.song = song

    def __str__(self):
        return f'Song {self.song} is not found in the songlist.'


class InvalidDifficulty(BaseException):
    def __init__(self):
        pass

    def __str__(self):
        return "草，诗人？"


class RoomIsFull(BaseException):
    def __init__(self):
        pass

    def __str__(self):
        return 'The room you are going to join is fuuuuullll.'


class QueryFailed(BaseException):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return 'Score query failed.'
