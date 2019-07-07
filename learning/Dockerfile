FROM jupyter/datascience-notebook

RUN mkdir -p /home

WORKDIR /home

# Copying over necessary files
COPY src ./src
COPY requirements.txt ./requirements.txt

# Installing packages and updating
RUN pip install -r ./requirements.txt
