#!/usr/bin/env bash

BASEDIR=$(dirname $0)
aws iam create-role --role-name legendre --assume-role-policy-document file://${BASEDIR}/lambda_role_policy.json 
aws iam put-role-policy --role-name legendre --policy-name ec2-access --policy-document file://${BASEDIR}/ec2_access.json
aws iam put-role-policy --role-name legendre --policy-name sns-access --policy-document file://${BASEDIR}/sns_access.json
aws iam create-instance-profile --instance-profile-name legendre
aws iam add-role-to-instance-profile --instance-profile-name legendre --role-name legendre
