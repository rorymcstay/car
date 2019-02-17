#!/usr/bin/env bash

images=()
while IFS= read -r line; do
    images+=( "$line" )
done < <( docker-compose config --services )

for image in "${images[@]}"; do
    aws ecr create-repository --repository-name $image --profile car_app --region us-east-1
done
