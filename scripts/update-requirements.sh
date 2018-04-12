#!/bin/sh -e

# requirements.txt

TMP_DIR=`mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir'`

echo "Creating $TMP_DIR..."
virtualenv "$TMP_DIR"
source "$TMP_DIR"/bin/activate

echo "Installing dependencies from setup.py..."
pip install .[zmq]
pip freeze | grep -v "^skygear==" > requirements.txt

echo "Cleaning up..."
rm -rf "$TMP_DIR"

# test_requirements.txt

TMP_DIR=`mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir'`

echo "Creating $TMP_DIR..."
virtualenv "$TMP_DIR"
source "$TMP_DIR"/bin/activate

echo "Installing test dependencies..."
pip install coverage isort lizard pylama pytest
pip freeze > test_requirements.txt

echo "Cleaning up..."
rm -rf "$TMP_DIR"
