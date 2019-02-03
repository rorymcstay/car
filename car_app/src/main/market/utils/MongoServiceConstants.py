import os


class MongoServiceConstants(object):
    def __init__(self):
        self.MARKETS = os.getenv('MARKET_DETAILS', 'marketDetails')
        self.COLLECTION_NAME = os.getenv("MONGO_COLLECTION", 'cars')
        self.DATABASE_NAME = os.getenv('MONGO_DATABASE', 'my_database')
        self.PASSWORD = os.getenv('MONGO_PASS', 'root')
        self.USERNAME = os.getenv('MONGO_USER', 'root')
        self.HOST = os.getenv('MONGO_HOST', '0.0.0.0:27017')
        self.TIMEOUT =os.getenv('MONGO_TIMEOUT', 10)
