import os

from influxdb import InfluxDBClient


class Monitoring:
    def __init__(self, thread):
        self.thread = thread
        self.client = InfluxDBClient(os.getenv('MONITOR_HOST', 'localhost'), os.getenv('8081'))

