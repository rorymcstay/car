# Classified car ad webscraper

This module is a webscraper for classified adverts of cars. Given a few
input parameters taken from the html source. A mapping module and a router
module. The app will traverse the website collecting cars in parrallel
using Workers. Each Worker controls a docker container with selenium standalone
chrome image.

## To start the application
1. build the image from the ```car``` directory.

        docker-compose build

2. start the service

        docker-compose up

This will start the donedeal feed, grafana and mongo-express.

## Pushing locally built images

locally built images can be pushed to the ecr repository after logging in by
running ```push.sh```

This will be soon setup to build images and publish them to the ecr on merges
to master. The ```car_platform``` repo is pulled onto a server and contains
the docker-compose configuration.

## Tests

<!--TODO externalise config for docker-compose to-->
<!--TODO externalise entrypoint remote url. This is docker engine-->
<!--TODO implement builder pattern/domain object-->
<!--TODO Main config map - the golden source per se for each container-->
<!--TODO Tidy up push to aws and other aws deployments-->
<!--TODO formalise mounting of docker compose keys: https://docs.docker.com/compose/compose-file/#variable-substitution->
<!--TODO market details object in constructor for market-->
<!--TODO simplify market constructor-->

## Delivery mechanism

## Request mechanism
You have to ask it for data items. It checks the cache
A request module which accepts requests and forwards it to server
