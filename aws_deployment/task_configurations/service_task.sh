#!/usr/bin/env bash

ecs-cli compose --project-name car-app --file external-services.yml --ecs-params external-services-config.yml --region us-west-2 create --launch-type FARGATE