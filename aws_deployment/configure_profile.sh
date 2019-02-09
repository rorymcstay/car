#!/usr/bin/env bash

CAR_KEY=fjtJYvwv50ZnUR4mVrhi2rhzOohI6ueoUSqWqdm+

CAR_USER=AKIAJX3CZLJ2ZFVZ25DQ

REGION=us-west-2

ecs-cli configure profile --profile-name car_app --access-key $CAR_USER --secret-key $CAR_KEY

aws configure --profile car_app --access-key $CAR_USER --secret-key $CAR_KEY --region $REGION
