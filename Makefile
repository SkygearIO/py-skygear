VERSION := $(shell git describe --always | sed 's/v\(.*\)/\1/')
PACKAGE_VERSION := $(shell echo $(VERSION) | sed 's/-\([0-9]*\)-\(g[0-9a-f]*\)/+\1.\2/')
DIST_DIR = ./dist/

.PHONY: build
build:
	python setup.py bdist_wheel
	python setup.py sdist

.PHONY: clean
clean:
	-rm -rf $(DIST_DIR)

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
