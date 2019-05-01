import bs4
from bs4 import ResultSet

from settings import markets, results
from src.main.car.Domain import Result


class ResultParser():
    
    def __init__(self, market, source):
        self.params = markets[market]
        self.items = results[market]
        self.soup = bs4.BeautifulSoup(source, "html.parser")
        self.results = self.soup.findAll(attrs=self.params['result'])
        
    def parseResults(self):
        all = []
        for result in results:
            for item in self.items:
                self.getItem(item, result)

            link = result.find("resultUrl")
            if link is None:
                link=result.find('a').attrs['href']
            else:
                link=link.find('a').attrs['href']
            img = [item.attrs['href'] for item in result.findAll(name=self.params['resultImg'])]
            text = result.text
            all.append(Result({"items": text.split('\n'), "img": img}, url=link))
        return all
    
    def getItem(self, item, start: ResultSet):
        items = {}
        for node in self.items[item]["nodes"][:-1]:
            start = start.findAll()

        if self.items[item]["single"]:
            start.find(**{self.params["last_nodeType"]: self.items[item]["nodes"][-1]})

            
        
    
    