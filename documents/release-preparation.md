# Notes for software release preparation

## Summary of release tasks

- [x] Feature freeze
- [x] Delete contents of build directory (ensure any old files are removed)
- [x] Clean old .pyc files - `clean.sh`
- [x] Regenerate test data (e.g. `makeinitsitedata.sh` or `maketestsitedata.sh`)
- [x] Local install
- [x] Run test suite
- [x] Update site data in local 'personal' installation
    - `annalist-manager initialize`
    - `annalist-manager updatesitedata`
- [x] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [x] Demo deployment; test
- [x] Documentation updates
- [x] Demo screencast update
- [x] Add TODO list to release notes
- [x] Create release preparation branch
    - `git checkout -b relprep-x.y.z develop`
    - *NOTE* use a different name to that which will be used to tag the release
- [x] Bump version to even value and update history
- [ ] Update version number in scripts, documents, etc.
    - [x] Release notes
    - [x] documents/installing-annalist.md
    - [x] documents/release-notes/announce_0.1.*.md
    - [x] documents/roadmap.md
    - [x] documents/pages/index.html
    - [x] src/annalist_root/annalist/__init__.py
    - [x] src/newkit_to_annalist_net.sh
    - [x] src/newkit_to_conina_ubuntu.sh
    - [x] Docker build scripts
- [x] Create new local installation and test again
- [x] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [x] Update front page link at annalist.net - copy `~annalist/uploads/pages/index.html` to `/var/www`
- [x] Update demo installation on annalist.net; test
    - `killall python`
    - `. anenv/bin/activate`
    - `pip uninstall annalist`
    - `pip install /var/www/software/Annalist-0.1.12.tar.gz --upgrade`
    - `annalist-manager runtests`
    - `. update-run-annalist.sh`
    - `cat annalist.out`
- [x] Commit changes
- [x] Upload to PyPI (see below)
- [x] Tag release on release branch
    - `git tag -a release-x.y.z`
- [x] Merge release branch to master
- [x] Test again on master branch
- [x] Push master branch, and tags
    - `git push --tags`
- [x] Merge release branch to develop
    - take care to ensure the branch is merged, not the tagged release
- [x] On develop branch, bump version number again (back to odd value)
- [x] Reset TODO list (remove entries moved to release notes, update version)
- [ ] Commit and push changes
- [ ] Delete release branch
    - `git branch -d release-x.y.z`
- [ ] Create Docker image, test (see below)
- [ ] Push docker image to DockerHub (see below)
- [ ] Post announcement to Google Group, Twitter and elsewhere

## Build kit and PyPI upload

Local:

    python setup.py clean --all
    python setup.py build
    python setup.py sdist
    python setup.py install

Register with PyPI:

    python setup.py register

Upload to PyPI:

    python setup.py sdist upload


## Create docker images

The following sequence must be run on any system with docker installed.  It assumes that the relevant version of Annalist has been installed and tested on the local system.

Use a well-connected Linux system for the following steps.

    cd ${ANNALIST}/src
    git checkout master
    git pull
    python setup.py clean --all
    python setup.py build
    python setup.py install
    annalist-manager version  # Check display

    cd ${ANNALIST}/src/docker/annalist-site
    make all
    make push

    cd ${ANNALIST}/src/docker/annalist
    make all
    make push

