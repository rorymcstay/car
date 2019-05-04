import json
from unittest import TestCase

from bson import ObjectId
from main.encoding import Encoder


class TestEncoder(TestCase):
    def test_default(self):
        """.default can serialise object id to string"""
        id = ObjectId()
        dic = {'_id': id, 'x': 1}
        result = json.dumps(dic, cls=Encoder)
        assert isinstance(result, str)

