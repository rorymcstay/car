#!/usr/bin/env bash

#(aws ecr get-login --no-include-email --region us-east-1 | sed 's|||')

images=()
while IFS= read -r line; do
    images+=( "$line" )
done < <( docker-compose config --services )

for image in "${images[@]}"; do
    docker tag $image:latest 064106913348.dkr.ecr.us-east-1.amazonaws.com/$image:latest
    docker push 064106913348.dkr.ecr.us-east-1.amazonaws.com/$image:latest
done

