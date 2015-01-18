BASE=ubuntu
IMAGE=annalist_site
# RELEASE=$(shell cat VERSION)
# RELEASE_PREFIX=
HOSTPORT=8000
GUESTPORT=8000

all: build

build: .build

.build: Dockerfile
	docker build --rm=true -t $(IMAGE) .
	touch .build

release: releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz

releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz: build VERSION
	echo "Releasing " $(RELEASE)
	git tag release/$(RELEASE)
	docker tag $(IMAGE) $(RELEASE_PREFIX)$(IMAGE):$(RELEASE)
	docker save $(RELEASE_PREFIX)$(IMAGE):$(RELEASE) > releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz

base-shell:
	docker run --rm -it $(BASE) bash

site-data:
	docker run --name=$(IMAGE) -d $(IMAGE)

run: build
	docker run --rm -it -p $(HOSTPORT):$(GUESTPORT) $(IMAGE)

shell: build
	docker run --rm -it $(IMAGE) bash

clean:
	$(RM) .build

.PHONY: clean release shell run start-db devserver base-shell build

