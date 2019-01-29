FROM python:3

RUN mkdir -p /home/src

WORKDIR /home

# Copying over necessary files
COPY src/main src/
COPY ./start.service ./
COPY requirements.txt ./

# The following is to install numpy
RUN apt-get dist-upgrade
RUN apt-get update
RUN apt-get -y install libc-dev
RUN apt-get -y install build-essential
RUN pip install -U pip

# Installing packages
RUN pip install -r ./requirements.txt

# Entrypoint
CMD ["python", "./start.service" ]
