import bs4

from settings import markets
from src.main.car.Domain import Result


class ResultParser():
    
    def __init__(self, market):
        self.params = markets[market]
        
    def parseResults(self, string):
        soup = bs4.BeautifulSoup(string, "html.parser")
        results = soup.findAll(attrs=self.params['result'])
        all = []
        for result in results:
            link = result.find("resultUrl")
            if link is None:
                link=result.find('a').attrs['href']
            else:
                link=link.find('a').attrs['href']
            img = [item.attrs['href'] for item in result.findAll(name=self.params['resultImg'])]
            text = result.text
            all.append(Result({"url": link, "text": text, "img": img}))
        return all
    