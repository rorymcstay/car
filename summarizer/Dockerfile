FROM python:3.6-alpine

RUN mkdir -p /home



WORKDIR /home

# Copying over necessary files
COPY src ./src

RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev
COPY requirements.txt ./requirements.txt
COPY settings.py ./settings.py
COPY summarizer.py ./app.py

RUN python -m pip install pip

# Installing packages
RUN pip install -r ./requirements.txt

# Entrypoint
CMD ["python", "./app.py" ]