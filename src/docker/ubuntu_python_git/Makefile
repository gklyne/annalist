BASE=ubuntu
IMAGE=ubuntu_python_git
# DATA_CONTAINER=annalist_site
# RELEASE=$(shell annalist-manager version)
# RELEASE_PREFIX=
HOSTPORT=8000
GUESTPORT=8000

base-shell:
	docker run --rm -it $(BASE) bash

clean:
	$(RM) .build

all: clean build

build: .build

.build: Dockerfile
	docker build --rm=false -t $(IMAGE) .
	touch .build

shell: build
	docker run --rm -it $(IMAGE) bash

# Declare non-file targets
.PHONY: base-shell all clean build shell
