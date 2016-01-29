BASE=ubuntu
IMAGE=annalist_site
DATA_CONTAINER=annalist_site
# RELEASE=$(shell cat VERSION)
# RELEASE_PREFIX=
HOSTPORT=8000
GUESTPORT=8000

base-shell:
	docker run --rm -it $(BASE) bash

shell: build
	docker run --rm -it $(IMAGE) bash

clean:
	$(RM) .build

all: clean build

build: .build

.build: Dockerfile
	docker build --rm=true -t $(IMAGE) .
	touch .build

site-data:
	docker run --name=$(DATA_CONTAINER) --detach=true $(IMAGE)

push: build
	# docker tag $(IMAGE):$(RELEASE) gklyne/$(IMAGE):$(RELEASE)
	# docker push gklyne/$(IMAGE):$(RELEASE)

	docker tag -f $(IMAGE) gklyne/$(IMAGE)
	docker push gklyne/$(IMAGE)

# Declare non-file targets
.PHONY: base-shell shell all clean build site-data push

