#!/usr/bin/env bash

. ./vars.sh

./package.sh

BASEDIR=$(dirname $0)
ROLE_ARN=$(aws iam get-role --role-name legendre |grep Arn| awk '{gsub(/"/, "", $2); print $2}')

# delete the function if it exists
aws lambda delete-function --function-name FindZombieInstances

aws lambda create-function \
--function-name FindZombieInstances  \
--region us-east-1 \
--zip-file fileb://$BASEDIR/legendre.zip \
--role $ROLE_ARN \
--handler legendre.handler \
--runtime python2.7  \
--timeout 30 \
--vpc-config SubnetIds=$SUBNET_ID,SecurityGroupIds=$SECURITY_GROUP_ID \
--memory-size 128