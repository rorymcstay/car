FROM python:2.7-alpine3.7

RUN mkdir -p /home/car

WORKDIR /home

COPY market ./car/
COPY service ./car/
COPY __init__.py ./car/
COPY ./requirements.txt ./car/requirements.txt
COPY start.service ./car/start.service

RUN pip install -r ./car/requirements.txt

CMD ["python", "./car/start.service" ]
