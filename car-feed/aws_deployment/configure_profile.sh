#!/usr/bin/env bash

CAR_KEY=fjtJYvwv50ZnUR4mVrhi2rhzOohI6ueoUSqWqdm+

CAR_USER=AKIAJX3CZLJ2ZFVZ25DQ

REGION=us-west-2


aws configure --profile car_app --access-key $CAR_USER --secret-key $CAR_KEY --region $REGION

# Make a docker engine and copy the bits to src

docker-machine create --driver amazonec2 --amazonec2-region us-west-2 --amazonec2-access-key $CAR_USER --amazonec2-secret-key $CAR_KEY  car-browsers

cd /Users/rorymcstay/.docker/machine/machines/

cp -r car-browsers /Users/rorymcstay/IdeaProjects/Car/car/car_app
