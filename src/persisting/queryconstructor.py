
class QueryConstructor:

    def __init__(self, values, names, parent):
        self.values = values
        self.query = {}
        self.names = names
        self.out = {}
        self.parent = parent

    def addToQuery(self, value, name):
        self.query[name] = value

    def main(self):
        for value, name in zip(self.values, self.names):
            self.addToQuery(value, name+'.'+self.parent)
        return self.out
    if __name__ == '__main__':
        main()
