#!/bin/sh

docker build -t oursky/pyourd:latest .
docker build -t oursky/pyourd:onbuild -f Dockerfile-onbuild .
