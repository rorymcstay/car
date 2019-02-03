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

# Install telegraf
RUN apt-get update
RUN wget https://dl.influxdata.com/telegraf/releases/telegraf_1.0.0_amd64.deb
RUN dpkg -i telegraf_1.0.0_amd64.deb
# Custom config
COPY telegraf.conf /etc/telegraf/telegraf.conf

# Make the wusgi log
RUN mkdir /var/log/uwsgi
RUN touch /var/log/uwsgi/uwsgi.log

# Custom Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf



# Installing packages
RUN pip install -r ./requirements.txt

# Entrypoint
CMD ["python", "./start.service" ]
