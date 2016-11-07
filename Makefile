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
