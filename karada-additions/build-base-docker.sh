#!/bin/bash

set -e

$(aws ecr get-login --no-include-email --region us-west-2 --profile karada-api) 
if [ -z ${BASE_TAG+x} ]; then BASE_TAG=latest; fi

echo $BASE_TAG
cd ..
docker build -t 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_karada_base:${BASE_TAG} . &&  docker push 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_karada_base:${BASE_TAG}
cd -
