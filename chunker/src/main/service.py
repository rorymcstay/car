import bs4
from bs4 import SoupStrainer, Tag
from kafka import KafkaProducer, KafkaConsumer

from settings import kafka_params


class Pagechunker():

    producer = KafkaProducer(**kafka_params)
    consumer = KafkaConsumer(**kafka_params)
    strainer = SoupStrainer()
    url = None
    def setUrl(self, url):
        self.url = url

    def streamChildren(self, tag: Tag):
        header = [("url", self.url)]
        for child in tag.children:
            payload = {
                "value": child
            }
            self.producer.send(topic="html-chunks", **payload,headers=header)
            if isinstance(child, Tag):
                self.streamChildren(tag)
            else:
                return

    def main(self):
        self.consumer.subscribe(["raw-page"])
        for page in self.consumer:
            soup = bs4.BeautifulSoup(page.value)
            for child in soup.children:
                self.streamChildren(child)
