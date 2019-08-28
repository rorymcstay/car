import json
import logging
import os
import traceback

import bs4
import requests
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor

from settings import nanny_params
from src.main.exceptions import ResultCollectionFailure
from src.main.tools import find


class ObjectParser:
    def __init__(self, feedName, source):
        self.params = requests.get(
            "http://{host}:{port}/{params_manager}/getParameter/mapper/{name}".format(**nanny_params,
                                                                                      name=feedName)).json()
        self.soup = bs4.BeautifulSoup(source, features="html.parser")

    def getRawJson(self, url):
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
                reportParameter('json_identifier')
                logging.warning("no result found")
            return out

        except Exception as e:
            traceback.print_exc()
            error = ResultCollectionFailure(url=url, reason=traceback.format_exc(), exception=e)
            raise error

    def normalizeJson(self, rawJson):
        item = {}
        for value in self.params["attrs"]:
            for val in rawJson:
                v = find(value["field"], val)
                item.update({value["name"]: list(v)})
                if v is None:
                    reportParameter("attrs.{}".format(value))
        return item




def reportParameter(parameter_key=None):
    endpoint = "http://{host}:{port}/parametermanager/{}/{}/{}".format(
        os.getenv("NAME"),
        parameter_key,
        "feed",
        **nanny_params
    )
    requests.get(endpoint)
