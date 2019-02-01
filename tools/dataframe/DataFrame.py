from client.Client import Client


class DataFrame:
    def __init__(self, make, model):
        self.client = Client('http://127.0.0.1:5000/query/cars/')
