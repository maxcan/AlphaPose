#!/bin/bash
set -o allexport; source .env; set +o allexport


docker build -t 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_aws_test:${TAG} --no-cache . &&  docker push 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_aws_test:${TAG}
