from src.main.mapping.DoneDeal import DoneDeal


class Mappers(object):
    def __init__(self):
        """
        Houses methods for mapping. Used to define the mapping implementation of a market class. Methods should be created
        in a seperate module and imported to this module. The method is added by defining a field _<name>_mapper to the
        function declaration.
        """
        self._donedeal_mapper = DoneDeal

    def __getitem__(self, item):
        return getattr(self, item)


mappers = Mappers()
