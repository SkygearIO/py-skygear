#!/bin/sh

docker build -t oursky/py-skygear:latest .
docker build -t oursky/py-skygear:onbuild -f Dockerfile-onbuild .
