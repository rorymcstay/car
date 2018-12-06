FROM python:2.7-alpine3.7

RUN mkdir -p /home/car

WORKDIR /home

COPY market ./car/
COPY service ./car/
COPY __init__.py ./car/
COPY requirements.txt ./car/requirements.txt

RUN pip install -r car/requirements.txt

CMD ["python", "start.service" ]
