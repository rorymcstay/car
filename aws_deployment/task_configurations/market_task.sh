#!/usr/bin/env bash

ecs-cli compose --project-name car-app --file market-loader.yml --ecs-params loader-config.yml --region us-west-2 create --launch-type FARGATE