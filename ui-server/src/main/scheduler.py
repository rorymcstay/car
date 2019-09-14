from docker import client as dockerClient
import sys
from datetime import datetime, timedelta

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from flask import request
from flask_classy import FlaskView, route
import json

from kafka import KafkaProducer

from settings import kafka_params, mongo_params

class ScheduledCollection:

    def __init__(self, feedName,**kwargs):
        self.feedName = feedName
        self.url = kwargs.get("url")
        self.trigger = kwargs.get("trigger")
        self.increment = kwargs.get("increment")
        self.increment_size = kwargs.get("increment_size")
        self.time_out = kwargs.get("time_out")


class JobExecutor:
    docker_client = dockerClient.from_env()
    producer = KafkaProducer(**kafka_params, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def startContainer(self, feedName):
        container = self.docker_client.containers.get(feedName)
        container.start()

    def publishUrl(self, feedName, url):
        item = {"url": url, "type": feedName}
        self.producer.send(topic="worker-queue".format(name=feedName),
                           value=item,
                           key=bytes(url, 'utf-8'))


class ScheduleManager(FlaskView):

    scheduler = BackgroundScheduler()
    job_store = MongoDBJobStore(**mongo_params)
    scheduler.add_jobstore(job_store)
    executor = JobExecutor()
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        scheduler.remove_all_jobs()
    scheduler.start()
    """
    If you schedule jobs in a persistent job store during your application’s initialization, you MUST define an explicit ID for the job and use replace_existing=True or you will get a new copy of the job every time your application restarts!Tip
    """
    @route("scheduleContainer/<string:feedName>", methods=["PUT"])
    def scheduleContainer(self, feedName):
        job = ScheduledCollection(feedName, **request.get_json())
        if job.trigger == 'in':
            timing = {
                "run_date": datetime.now() + timedelta(**{job.increment: int(job.increment_size)})
            }
        else:
            timing = {
                job.increment: int(job.increment_size),
            }
        self.scheduler.add_job(self.executor.startContainer, job.trigger, args=[feedName], id=feedName, replace_existing=True,**timing)
        return 'ok'

    @route("addJob/<string:feedName>",methods=["PUT"])
    def addJob(self, feedName):
        job = ScheduledCollection(feedName, **request.get_json())
        timing = {
            job.increment_size: job.increment,
            "run_date": datetime.now() + timedelta(**{job.increment: int(job.increment_size)})
        }
        self.scheduler.add_job(self.executor.publishUrl, job.trigger, args=[feedName, job.url], id=job.url, **timing)

    def getStatus(self):
        isRunning = self.scheduler.running
        jobs = self.scheduler.get_jobs()
        payload = {"isRunning": isRunning, "jobs": jobs}
        return json.dumps(payload)
