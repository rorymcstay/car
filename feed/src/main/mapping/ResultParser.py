import bs4
from bs4 import ResultSet

from settings import markets, results
from src.main.car.Domain import Result


class ResultParser:
    
    def __init__(self, market, source):
        self.params = markets[market]
        self.items = results[market]
        self.soup = bs4.BeautifulSoup(source, "html.parser")
        self.results = self.soup.findAll(attrs=self.params['result'])
        
    def parseResults(self):
        all = []
        for result in results:
            items = {}
            for item in self.items:
                items.update(self.getItem(item, result))
            all.append(Result(items))
        return all
    
    def getItem(self, item: str, start: ResultSet) -> dict:
        """
        This function assumes it is starting from a single result node extracted from a list
        :param item: the name of the item to get in the settings/results dict
        :param start: the node to start from
        :return:
        """
        path = self.items[item]

        for node in path["class"]:
            start = start.findAll(attrs=node)
        if path['single'] and path['attr']:

        elif len(path['class']) == 0:
            start = start.findAll(attrs=path["class"][-1])
        if path["attr"] is None:
            if path['single']:
                finish = start.text
            else:
                finish = [st.text for st in start]
        else:
            if path['single']:
                finish = start['attrs'][path['attrs']]
            else:
                finish = [t['attrs'][path['attrs']] for t in start]
        return {item: finish}

if __name__ == '__main__':
    with open('test.html') as file:
        source = file.read()
    rp = ResultParser('donedeal', source)
    rp.parseResults()
