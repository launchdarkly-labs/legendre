#!/usr/bin/env bash
mkdir -p dist
rm -rf dist/*
rm legendre.zip

cp *.py dist
pip install -r requirements.txt -t dist

(cd dist && zip ../legendre *)
