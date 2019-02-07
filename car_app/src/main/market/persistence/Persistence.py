import hashlib
import json
import traceback
from datetime import datetime
from bson import ObjectId

import logging as log

from utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='persistence')

class Persistence:
    def __init__(self, market):
        self.market = market
        self.client = market.service

    def save_market_details(self):
        """update its market details to in the mongo database """
        self.client.save_market_details(name=self.market.name, market_definition={'market': self.market.name})

    def save_progress(self):
        """saves the last page it went to with date and the cars it collected from that page"""
        id = hashlib.sha3_224(self.market.name.encode('utf-8')).hexdigest()
        id = id[:24]
        progress = {'_id': ObjectId(id),
                    'latest_result_page': self.market.webCrawler.driver.current_url,
                    'latest_processing': [w.webCrawler.driver.current_url for w in self.market.workers],
                    'time_stamp': str(datetime.utcnow())}
        self.client.db['progress'].replace_one({'_id': ObjectId(id)}, progress)

    def return_to_previous(self):
        """ goes to the last visited page and then traverses until one of the latest results is in its queue """
        try:
            id = hashlib.sha3_224(self.market.name.encode('utf-8')).hexdigest()
            id = id[:24]
            x = self.client['progress'].find_one({'_id': ObjectId(id)})
            progress = json.loads(x)
        except Exception:
            write_log(LOG.warning, msg="Failed to load latest progress - returning to home")
            self.market.webCrawler.driver.get(self.market.home)
            return
        self.market.webCrawler.driver.get(self.market.home)
        results = self.market.webCrawler.get_result_array()
        try:
            while not any(result in progress['latest_processing'] for result in results):
                self.market.webCrawler.next_page()
                results = self.market.webCrawler.get_result_array()
        except Exception:
            write_log(LOG.info,msg="Error going to last page of results. Starting from {}".format(self.market.webCrawler.current_url))
            traceback.print_exc()
