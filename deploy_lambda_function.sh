#!/usr/bin/env bash

. ./vars.sh

./package.sh

PYTHONPATH=./dist:$PYTHONPATH python scripts/setup_lambda.py