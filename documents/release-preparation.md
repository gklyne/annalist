# Notes for software release preparation

## Summary of release tasks

- [ ] Feature freeze
- [ ] Uninstall annalist (if installed): `pip uninstall annalist`
- [ ] Delete contents of build directory (ensure any old files are removed)
- [ ] Clean old .pyc files - `clean.sh`
- [ ] Local install
- [ ] Run test suite
- [ ] Update site data in local 'personal' installation
    - `annalist-manager initialize` (is this really needed?  does it wipe users?  No)
    - `annalist-manager updatesitedata`
- [ ] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [ ] Documentation updates
- [ ] Demo screencast update

- [x] Create release preparation branch
    - `git checkout -b release-prep-x.y.z develop`
    - *NOTE* use a different name to that which will be used to tag the release
- [x] Add TODO list to release notes (edit out working notes)
- [x] Bump version to even value in `src/annalist_root/annalist/__init__.py`
- [x] Bump data compatibility version if new data is not compatible with older releases
- [x] Regenerate test data (e.g. `makeinitsitedata.sh` or `maketestsitedata.sh`)
- [x] Reinstall and re-run test suite
- [x] Add release highlights description to release notes
- [x] Review issues list in GitHub
- [x] Review roadmap (`documents/roadmap.md`)
- [x] Update version number in scripts, documents, etc.
    - [x] Release notes
    - [x] documents/installing-annalist.md
    - [x] documents/roadmap.md
    - [x] documents/pages/index.html
    - [x] src/newkit_to_annalist_net.sh
    - [x] src/newkit_to_conina_ubuntu.sh
    - [x] Docker build scripts
- [x] Create announcement text in `documents/release-notes/announce_0.1.*.md`
- [x] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [x] Update demo installation on annalist.net; test
    - ssh to annalist@annalist.net
    - `killall python`
    - `. anenv/bin/activate`
    - `pip uninstall annalist`
    - `pip install /var/www/software/Annalist-0.1.xx.tar.gz --upgrade`
    - `annalist-manager runtests`
    - `. update-run-annalist.sh`
    - `cat annalist.out`
- [x] Update front page link at annalist.net - copy `~annalist/uploads/pages/index.html` to `/var/www`
        cp ~annalist/uploads/pages/index.html /var/www
- [x] Commit changes
- [x] Upload to PyPI (see below)
- [ ] Tag release on release branch
    - `git tag -a release-x.y.z`
- [ ] Merge release branch to master
    - e.g.
        - `git checkout master`
        - `git merge release-prep-x.y.z`
- [ ] Test again on master branch
- [ ] Push master branch, and tags
    - `git push`
    - `git push --tags`
- [ ] Merge release branch to develop
    - take care to ensure the branch is merged, not the tagged release
    - e.g.
        - `git checkout develop`
        - `git merge release-prep-x.y.z`
- [ ] On develop branch, bump version number again (back to odd value)
- [ ] Reset TODO list (remove entries moved to release notes, update version)
- [ ] Commit and push changes
- [ ] Delete release branch
    - `git branch -d release-prep-x.y.z`
- [ ] Create Docker image, test (see below)
- [ ] Push docker image to DockerHub (see below)
- [ ] Post announcement to Google Group, Twitter and elsewhere
- [ ] Regenerate test data (e.g. `makeinitsitedata.sh` or `maketestsitedata.sh`), retest


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

The following sequence must be run on any system with docker installed (cf. ssh-dev-annalist.sh).  It assumes that the relevant version of Annalist has been installed and tested on the local system.

Use a well-connected Linux system for the following steps, and set the python virtual environment.

    cd ${ANNALIST}/src
    git checkout master
    git pull
    pip uninstall annalist
    python setup.py clean --all
    python setup.py build
    python setup.py install
    annalist-manager version  # Check display

    cd ${ANNALIST}/src/docker/annalist_site
    make all
    make push

    cd ${ANNALIST}/src/docker/annalist
    make all
    make push

See [installing-annalist.md](installing-annalist.md) for details of how to run and test the resulting container.

