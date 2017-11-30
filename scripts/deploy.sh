#!/bin/bash -e

docker login -u "$DOCKER_HUB_USER" -p "$DOCKER_HUB_PASSWORD"
docker login -u "$QUAY_USER" -p "$QUAY_PASSWORD" quay.io

MAKE="make -C scripts/docker-images/release"

$MAKE clean
$MAKE wheel docker-build

# Push git-sha-tagged image
$MAKE docker-push DOCKER_REGISTRY=quay.io/

# Push tag/branch image
if [ -n "$TRAVIS_TAG" ]; then
    $MAKE docker-push-version PUSH_DOCKER_TAG="${TRAVIS_TAG}"
    $MAKE docker-push-version DOCKER_REGISTRY=quay.io/ PUSH_DOCKER_TAG="${TRAVIS_TAG}"
    generate-python-doc  --pwd $PWD
    publish-doc --platform python --pwd $PWD  --doc-dir $PWD/docs/_build --bucket 'docs.skygear.io' --prefix '/py/reference' --version $TRAVIS_TAG --distribution-id E31J8XF8IPV2V
else
    $MAKE docker-push-version PUSH_DOCKER_TAG="${TRAVIS_BRANCH/master/canary}"
    $MAKE docker-push-version DOCKER_REGISTRY=quay.io/ PUSH_DOCKER_TAG="${TRAVIS_BRANCH/master/canary}"
    generate-python-doc  --pwd $PWD
    publish-doc --platform python --pwd $PWD  --doc-dir $PWD/docs/_build --bucket 'docs.skygear.io' --prefix '/py/reference' --version $TRAVIS_BRANCH --distribution-id E31J8XF8IPV2V
fi
