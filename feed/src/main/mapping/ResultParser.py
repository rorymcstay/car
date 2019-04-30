import bs4

from settings import markets
from src.main.car.Domain import Result


class ResultParser():
    
    def __init__(self, market):
        self.params = markets[market]
        
    def parseResults(self, string):
        soup = bs4.BeautifulSoup(string, "html.parser")
        result = soup.findAll(self.params['result'])
        link = result.find("resultUrl")
        if len(link) == 1:
            link = link.attrs['href']
        else:
            link = result.attrs['href']
        img = result.find(self.params['resultImg'])
        
        text = result.text
        Result({"url": link, "text": text})
               
    