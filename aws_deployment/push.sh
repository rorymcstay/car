#!/usr/bin/env bash

docker-compose build

images=()
while IFS= read -r line; do
    images+=( "$line" )
done < <( docker-compose config --services )

for image in "${images[@]}"; do
    docker tag $image 064106913348.dkr.ecr.us-west-2.amazonaws.com/car-images/$image:latest
    docker push 064106913348.dkr.ecr.us-west-2.amazonaws.com/car-images/$image:latest
done
