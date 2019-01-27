FROM python:2.7-alpine3.7

RUN mkdir -p /home/src

WORKDIR /home

COPY src/main src/
COPY ./start.service ./
COPY requirements.txt ./

RUN pip install -r ./requirements.txt

CMD ["python", "./start.service" ]
