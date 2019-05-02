import json
from typing import List, Dict, Any, Union

import bs4
from bs4 import Tag, NavigableString

from settings import markets, results
from src.main.car.Domain import Result


class ResultParser:
    
    items: Union[Result, List[Result], Dict[
        str, Union[Dict[str, Union[List[str], bool, str]], Dict[str, Union[List[str], bool, None, str]]]], Dict[
                     str, Union[
                         Dict[str, Union[List[Any], bool, str]], Dict[str, Union[List[str], bool, None, str]], Dict[
                             str, Union[List[str], bool, str]]]]]

    def __init__(self, market, source):
        self.params = markets[market]
        self.items = results[market]
        self.soup = bs4.BeautifulSoup(source, "html.parser")
        self.results = self.soup.findAll(attrs=self.params['result'])
        
    def parseResults(self):
        all = []
        for result in self.results:
            items = {}
            for item in self.items:
                items.update(self.getItem(item, result))
            all.append(Result(items))
        return all
    
    def getItem(self, item: str, start: Tag) -> dict:
        """
        This function assumes it is starting from a single result node extracted from a list
        :param item: the name of the item to get in the settings/results dict
        :param start: the node to start from
        :return:
        """
        path = self.items[item]

        if path['attr'] and path['single']:
            for step in path['class']:
                startTent = start.findAll(attrs={"class": step})
                if len(startTent) > 0:
                    start = startTent[0]
            try:
                # if this doesnt work get the children... eg a photo tag
                finish = start.attrs[path['attr']]
            except:
                finish = [node if isinstance(node, NavigableString) or node is None else node.attrs.get(path['attr']) for node in start.children]
        elif path['attr'] and not path['single']:
            for step in path['class'][:-1]:
                start = start.findAll(attrs={"class": step})[0]
            if len(path['class']) > 0:
                start.findAll(attrs={"class": path["class"][-1]})
            finish = [sta.attrs.get(path['attr']) if isinstance(sta, Tag) else sta for sta in start]
        # attrs will not come past here
        elif path['single']:
            for node in path["class"]:
                start = start.find(attrs={"class": node})
            finish = start.text if start is not None else None
        else:
            for node in path["class"]:
                start = start.find(attrs={"class": node})
            if start is not None:
                finish = [node if isinstance(node, NavigableString) or node is None else node.text for node in start.children]
            else:
                finish = None
        return {item: finish}


if __name__ == '__main__':
    with open('test.html') as file:
        source = file.read()
    rp = ResultParser('piston_heads', source)
    results = rp.parseResults()
    print(json.dumps([result.__dict__() for result in results], indent=4))
