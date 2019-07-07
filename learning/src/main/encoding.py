from json import JSONEncoder

from bson import ObjectId


class Encoder(JSONEncoder):
    """
    Extends JSONEncoder so that ~bson.ObjectId can be serialised to a string
    """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(0)
        else:
            return JSONEncoder.default(self, o)
