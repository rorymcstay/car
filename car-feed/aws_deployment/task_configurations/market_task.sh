#!/usr/bin/env bash

#ecs-cli configure --cluster car-cluster --region us-west-2 --default-launch-type FARGATE --config-name car-cluster

ecs-cli compose  --file ./market-loader.yml --project-name car-feed --ecs-params ./loader-config.yml --cluster-config car-cluster service create