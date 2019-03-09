#!/bin/bash

set -o allexport; source .env; set +o allexport
env

nvidia-docker run  --env-file .env -it 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_aws_test:${TAG} python3 aws.py
