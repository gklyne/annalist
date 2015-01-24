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

all: build

build: .build

.build: Dockerfile
	docker build --rm=true -t $(IMAGE) .
	touch .build

site-data:
	docker run --name=$(DATA_CONTAINER) -d $(IMAGE)

# run: build
# 	docker run --rm -it -p $(HOSTPORT):$(GUESTPORT) $(IMAGE)

# release: releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz

# releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz: build VERSION
# 	echo "Releasing " $(RELEASE)
# 	git tag release/$(RELEASE)
# 	docker tag $(IMAGE) $(RELEASE_PREFIX)$(IMAGE):$(RELEASE)
# 	docker save $(RELEASE_PREFIX)$(IMAGE):$(RELEASE) > releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz

.PHONY: clean release shell run start-db devserver base-shell build

# Declare non-file targets
.PHONY: base-shell shell all clean build site-data
