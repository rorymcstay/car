FROM python:3

RUN mkdir -p /home

WORKDIR /home

# Copying over necessary files
COPY src ./src
COPY src/entrypoints ./src/entrypoints

COPY requirements.txt ./requirements.txt

# The following is to install numpy on full linux
RUN apt-get dist-upgrade
RUN apt-get update
RUN apt-get -y install libc-dev
RUN apt-get -y install build-essential
RUN pip install -U pip

# Installing packages
RUN pip install -r ./requirements.txt

# Entrypoint
CMD ["python", "./src/entrypoints/DoneDealFeed.py" ]