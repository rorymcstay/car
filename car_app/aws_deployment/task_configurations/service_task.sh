#!/usr/bin/env bash

bucket_name=car-kubernetes-state

#bucket for statebgdfbbd g
aws s3api create-bucket \
--bucket car-kubernetes-state \
--region us-east-1

#versioning
aws s3api put-bucket-versioning --bucket car-kubernetes-state --versioning-configuration Status=Enabled

kops create cluster \
--node-count=3 \
--node-size=t2.medium \
--zones=us-east-1a \
--name=car-cluster

