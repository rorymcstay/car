FROM python:3.6-alpine

RUN mkdir -p /home

WORKDIR /home

# Copying over necessary files
COPY src ./src

COPY requirements.txt ./requirements.txt
COPY settings.py ./settings.py
COPY peristence.py ./app.py

RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add postgresql-dev
RUN pip install --upgrade pip
# Installing packages
RUN pip install -r requirements.txt
RUN apk del build-deps

EXPOSE 5006

# Entrypoint
CMD ["python", "./app.py" ]