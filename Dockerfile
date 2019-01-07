FROM python:2.7-alpine3.7

RUN mkdir -p /home/car

WORKDIR /home

COPY market ./car/
COPY service ./car/
COPY __init__.py ./car/
COPY ./requirements.txt ./car/requirements.txt
COPY start.service ./car/start.service

WORKDIR ./car

RUN pip install -r ./requirements.txt

CMD ["python", "./start.service" ]
