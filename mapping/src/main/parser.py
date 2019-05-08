import json
import traceback

import bs4
from bs4 import Tag, NavigableString
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor

from settings import feeds, summary_feeds
from src.main.exceptions import ResultCollectionFailure
from src.main.tools import find


class ResultParser:

    def __init__(self, feedName, source):
        self.params = summary_feeds[feedName]
        self.soup = bs4.BeautifulSoup(source, "html.parser")

    def parseResult(self):
        items = {}
        for item in self.params:
            items.update(self.getItem(item, self.soup))
        return items

    def getItem(self, item: str, start: Tag) -> dict:
        """
        This function assumes it is starting from a single result node extracted from a list
        :param item: the name of the item to get in the settings/results dict
        :param start: the node to start from
        :return:
        """
        path = self.params[item]

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


class ObjectParser:
    def __init__(self, feedName, source):
        self.params = feeds[feedName]
        self.soup = bs4.BeautifulSoup(source, "html.parser")

    def getItem(self, url):
        """
        attempts to get car from current page source, returns to the previous set of results in which it came
        :return:
        """
        soup = self.soup

        out = []
        try:
            # Find all script objects
            for script in soup.find_all('script'):
                # and check which one containse the unique json variable name
                if self.params['json_identifier'] in script.text:
                    # then use the javascript parser to find the variable called json_identifier
                    tree = JavascriptParser().parse(script.text)
                    script_objects = next(node.right for node in nodevisitor.visit(tree)
                                          if (isinstance(node, ast.Assign) and
                                              node.left.to_ecma() == self.params['json_identifier']))
                    raw_car = json.loads(script_objects.to_ecma())
                    # add it to list to verify its a single result
                    out.append(raw_car)
            if len(out) == 0:
                raise ResultCollectionFailure(reason="Nothing found here", url=url, exception=None)
            else:
                item = {}
                for name in self.params["attrs"]:
                    for val in out:
                        item.update(find(self.params["attrs"][name], val))
                return item
        except Exception as e:
            traceback.print_exc()
            error = ResultCollectionFailure(url=url, reason=traceback.format_exc(),exception=e)
            raise error


if __name__ == '__main__':
    with open('test.html') as file:
        source = file.read()
    rp = ResultParser('piston_heads', source)
    results = rp.parseResults()
    print(json.dumps([result for result in results], indent=4))
