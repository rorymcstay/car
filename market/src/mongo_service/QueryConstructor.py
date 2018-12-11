
class QueryConstructor:

    def __init__(self, values, names, parent):
        """
        Constructs a query which returns a dictionary of specific values.

        :param values: An array of values in order of names
        :param names: An array of attribute names in order of values
        :param parent: The parent object in which the names occur
        """
        self.values = values
        self.query = {}
        self.names = names
        self.parent = parent
        self.projection = {}
        for value, name in zip(self.values, self.names):
            self.add_to_query(value, name + '.' + self.parent)

    def add_to_query(self, value, name):
        """And a criteria to the query"""
        self.query[name] = value

    def make_projection(self, values):
        """

        :param values: An array of fields to return
        :return:
        """
        for value in values:
            self.add_to_projection(self.parent + '.' + value)

    def add_to_projection(self, item_to_include):
        self.projection[item_to_include] = 1

