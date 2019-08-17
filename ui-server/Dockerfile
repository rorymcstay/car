FROM python:3.6-alpine

RUN mkdir -p /home

WORKDIR /home

# Copying over necessary files
COPY src ./src

COPY requirements.txt ./requirements.txt
COPY settings.py ./settings.py
COPY ui-server.py ./app.py

RUN python -m pip install pip
# Installing packages
RUN pip install -r ./requirements.txt

# Entrypoint
CMD ["python", "./app.py" ]