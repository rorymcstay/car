import logging as log
import os
import traceback
from datetime import datetime

from bson import ObjectId

from src.main.car.Domain import make_id
from src.main.service.mongo_service.MongoService import MongoService
from src.main.utils.LogGenerator import LogGenerator, write_log

LOG = LogGenerator(log, name='persistence')


class Persistence:
    id: ObjectId
    client: MongoService

    def __init__(self, market):
        self.market = market
        self.client = market.mongoService
        self.id = make_id(self.market.name)

    def save_market_details(self):
        """update its market details to in the mongo database """
        self.client.save_market_details(name=self.market.name, market_definition={'market': self.market.name})

    def save_progress(self):
        """saves the last page it went to with date and the cars it collected from that page"""

        progress = {'_id': self.id,
                    'latest_result_page': self.market.webCrawler.driver.current_url,
                    'latest_processing': self.market.results,
                    'time_stamp': str(datetime.utcnow())}

        x = self.client.db['progress'].find_one({'_id': self.id})
        if x is None:
            self.client.db['progress'].insert_one(progress)
        else:
            self.client.db['progress'].replace_one({'_id': self.id}, progress)

    def return_to_previous(self):
        """ goes to the last visited page and then traverses until one of the latest results is in its queue """
        try:
            progress = self.client.db['progress'].find_one({'_id': self.id})
        except Exception:
            traceback.print_exc()
            write_log(LOG.warning, msg="Failed to load latest progress - returning to home")
            self.market.webCrawler.driver.get(self.market.home)
            return
        if progress is None:
            self.market.webCrawler.driver.get(self.market.home)
            return
        self.market.webCrawler.driver.get(progress['latest_result_page'])
        results = self.market.webCrawler.get_result_array()
        try:
            count=0
            while os.getenv('TRAVERSE', False) and not any(result in progress['latest_processing'] for result in results):
                self.market.webCrawler.next_page()
                results_to_check = self.market.webCrawler.get_result_array()
                if any(result in progress['latest_processing'] for result in results_to_check):
                    write_log(LOG.info, msg="found_last_place", attemps=count)
                    return
                else:
                    count += 1
                    write_log(LOG.info, msg="going_next", attemps=count)
                    continue
        except Exception:
            write_log(LOG.info, msg="Error going to last page of results. Starting from {}".format(self.market.webCrawler.current_url))
            traceback.print_exc()
