DIST_DIR = ./dist/
DIST := skygear-server
VERSION := $(shell git describe --always --tags)

.PHONY: build
build:
	python setup.py bdist_wheel
	python setup.py sdist

.PHONY: clean
	-rm -rf $(DIST_DIR)

.PHONY: docker-build
docker-build: build
	cp skygear-server scripts/release/
	make -C scripts/release docker-build

.PHONY: docker-build
docker-push:
	make -C scripts/release docker-push
