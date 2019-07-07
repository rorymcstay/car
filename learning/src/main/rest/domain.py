import hashlib
from datetime import time

from bson import ObjectId


class Session:
    """The session object which must be sent along with the body of every request to ensure user is logged in"""


    def __init__(self, username, password):
        self._id = username
        self.password = password
        self.serverTime = time()

    def make_id(self, string) -> ObjectId:
        id = hashlib.sha3_224(string.encode('utf-8')).hexdigest()
        id = id[:24]
        return ObjectId(id)
