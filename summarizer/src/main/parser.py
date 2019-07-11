import bs4
import requests
from bs4 import Tag, NavigableString

from settings import nanny_params


class ResultParser:

    def __init__(self, feedName, source):
        r = requests.get(
            "http://{host}:{port}/parametercontroller/getParameter/summarizer/{name}".format(**nanny_params,
                                                                                              name=feedName))
        self.params = r.json()
        self.soup = bs4.BeautifulSoup(source, "html.parser")

    def parseResult(self):
        items = {}
        self.params.pop("name")
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
                finish = [node if isinstance(node, NavigableString) or node is None else node.attrs.get(path['attr'])
                          for node in start.children]
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
                finish = [node if isinstance(node, NavigableString) or node is None else node.text for node in
                          start.children]
            else:
                finish = None
        return {item: finish}
