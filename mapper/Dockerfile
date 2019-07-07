FROM python:3.6-alpine

RUN mkdir -p /home

WORKDIR /home

# Copying over necessary files
COPY src ./src

COPY requirements.txt ./requirements.txt
COPY settings.py ./settings.py
COPY app.py ./app.py

# Installing packages
RUN pip install -r ./requirements.txt

# Entrypoint
CMD ["python", "./app.py" ]