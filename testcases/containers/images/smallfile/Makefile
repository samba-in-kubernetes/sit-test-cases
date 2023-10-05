CONTAINER_NAME := sit-test-cases:smallfiles

build:
	podman build . -t $(CONTAINER_NAME)

push:
	podman push $(CONTAINER_NAME) quay.io/samba.org/$(CONTAINER_NAME)

clean:
	podman rmi --force $(CONTAINER_NAME)
