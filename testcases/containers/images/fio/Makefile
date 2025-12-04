CONTAINER_CMD ?= podman
IMG_PREFIX := quay.io/samba.org/sit-test-cases
IMG_TAG := fio
IMG := $(IMG_PREFIX):$(IMG_TAG)


build:
	$(CONTAINER_CMD) build --file $(CURDIR)/Containerfile --tag $(IMG)

push:
	$(CONTAINER_CMD) push $(IMG)

clean:
	$(CONTAINER_CMD) rmi --force $(IMG)

