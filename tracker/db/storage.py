import ujson
from pydantic import parse_obj_as

from tracker.configs import settings
from tracker.structs import User


class JSONStorage:
    def __init__(self):
        self.file = settings.DB_FILE

        with open(self.file, "r+") as _file:
            data = "\n".join(_file.readlines())
        with open(self.file, "w+") as _file:
            ujson.dump(ujson.loads(data or "{}"), _file)

    def get_or_create_user(self, tid: int) -> User:
        with open(self.file, "r+") as _file:
            result = ujson.load(_file)

        user = result.get(str(tid))
        return parse_obj_as(User, user) if user else self.create_user(User(tid=tid))

    def create_user(self, user: User) -> User:
        with open(self.file, "r+") as _file:
            db = ujson.load(_file)

        db[str(user.tid)] = user.dict()
        with open(self.file, "w+") as _file:
            ujson.dump(db, _file)
        return user


storage = JSONStorage()
