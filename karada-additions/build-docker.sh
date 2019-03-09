#/bin/bash


docker build -t 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_aws_test:${TAG} . &&  docker push 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_aws_test:${TAG}