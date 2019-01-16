from car.src.market import DoneDeal


class Mappers(object):
    def __init__(self):
        self._donedeal_mapper = DoneDeal

    def __getitem__(self, item):
        return getattr(self, item)


mappers = Mappers()
