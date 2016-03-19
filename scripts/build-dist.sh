#!/bin/bash -e

PACKAGE_VERSION=`git describe --tags | sed 's/v\(.*\)/\1/' | sed 's/-\([0-9]*\)-\(g[0-9a-f]*\)/+\1.\2/'`

sed -i "s/version='.*'/version='$PACKAGE_VERSION'/" setup.py

python setup.py bdist_wheel
python setup.py sdist
