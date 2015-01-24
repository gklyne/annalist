BASE=ubuntu
IMAGE=annalist_dev
DATA_CONTAINER=annalist_site
RELEASE=$(shell annalist-manager version)
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
	docker build --rm=true -t $(IMAGE):$(RELEASE) .
	touch .build

run: build
	# docker run --rm -it -p $(HOSTPORT):$(GUESTPORT) $(IMAGE)
	docker run --rm -it -p $(HOSTPORT):$(GUESTPORT) --volumes-from=$(DATA_CONTAINER) $(IMAGE):$(RELEASE)

# site-data:
# 	docker run --name=$(IMAGE) -d $(IMAGE)

# release: releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz

# releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz: build VERSION
# 	echo "Releasing " $(RELEASE)
# 	git tag release/$(RELEASE)
# 	docker tag $(IMAGE) $(RELEASE_PREFIX)$(IMAGE):$(RELEASE)
# 	docker save $(RELEASE_PREFIX)$(IMAGE):$(RELEASE) > releases/$(RELEASE_PREFIX)$(IMAGE)-$(RELEASE).tar.gz

# Declare non-file targets
.PHONY: base-shell shell all clean build run 

