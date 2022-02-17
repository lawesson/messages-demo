export DOCKER_IMAGE ?= messagesdemo:latest
DC=docker-compose -f docker/docker-compose.yaml

.PHONY: image
image:
	docker build . -f docker/Dockerfile -t ${DOCKER_IMAGE}


.PHONY: run
run: image
	${DC} run messagebroker migrate
	${DC} run -p 8080:80 messagebroker


.PHONY: runserver
runserver:
	./manage.py migrate
	./manage.py runserver


.PHONY: clean
clean:
	${DC} stop
	${DC} rm -f


.PHONY: testimage
testimage: image
	docker run --rm ${DOCKER_IMAGE} test