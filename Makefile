VERSION := $(shell git describe --always | sed 's/v\(.*\)/\1/')
PACKAGE_VERSION ?= $(shell echo $(VERSION) | sed 's/-\([0-9]*\)-\(g[0-9a-f]*\)/+\1.\2/')
DIST_DIR = ./dist/
OS = $(shell uname -s)

ifeq ($(OS),Darwin)
	SED := sed -i ""
else
	SED := sed -i""
endif

DOCKER_COMPOSE_CMD_TEST := docker-compose \
	-f docker-compose.test.yml

DOCKER_RUN_TEST := ${DOCKER_COMPOSE_CMD_TEST} run --rm test-app

.PHONY: build
build:
	python setup.py bdist_wheel
	python setup.py sdist

.PHONY: clean
clean:
	-rm -rf $(DIST_DIR)

.PHONY: before-docker-test
before-docker-test:
	${DOCKER_COMPOSE_CMD_TEST} up -d test-db
	sleep 20
	${DOCKER_COMPOSE_CMD_TEST} exec test-db \
		psql -c 'CREATE DATABASE skygear_test;' -U postgres
	${DOCKER_COMPOSE_CMD_TEST} exec test-db \
		psql -c 'CREATE EXTENSION postgis;' -U postgres -d skygear_test

.PHONY: docker-just-test
docker-just-test:
	${DOCKER_RUN_TEST} pylama skygear
	${DOCKER_RUN_TEST} coverage run --source skygear setup.py test
	${DOCKER_RUN_TEST} coverage report -m --omit '*tests*'

.PHONY: after-docker-test
after-docker-test:
	${DOCKER_COMPOSE_CMD_TEST} down -v

.PHONY: docker-test
docker-test: before-docker-test docker-just-test after-docker-test

.PHONY: docker-build
docker-build: build
	cp skygear-server scripts/release/
	make -C scripts/docker-images/release docker-build

.PHONY: docker-build
docker-push:
	make -C scripts/docker-images/release docker-push

.PHONY: release-commit
release-commit:
	./scripts/release-commit.sh

.PHONY: update-version
update-version:
	$(SED) "s/version='.*'/version='$(PACKAGE_VERSION)'/" setup.py
	$(SED) "s/__version__ = '.*'/__version__ = '$(PACKAGE_VERSION)'/" skygear/__version__.py
