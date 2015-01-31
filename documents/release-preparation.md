# Notes for software release preparation

## Summary of release tasks

- [ ] Feature freeze
- [ ] Delete contents of build directory (ensure any old files are removed)
- [ ] Clean old .pyc files - `clean.sh`
- [ ] Regenerate test data (e.g. `makeinitsitedata.sh` or `maketestsitedata.sh`)
- [ ] Local install
- [ ] Run test suite
- [ ] Update site data in local 'personal' installation
    - `annalist-manager initialize`
    - `annalist-manager updatesitedata`
- [ ] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [ ] Demo deployment; test
- [ ] Documentation updates
- [ ] Demo screencast update
- [ ] Add TODO list to release notes, and reset
- [ ] Bump version to even value and update history
- [ ] Update version number in scripts, documents, etc.
    - [ ] TODO
    - [ ] Release notes
    - [ ] documents/installing-annalist.md
    - [ ] documents/release-notes/announce_0.1.*.md
    - [ ] documents/roadmap.md
    - [ ] documents/pages/index.html
    - [ ] src/annalist_root/annalist/__init__.py
    - [ ] src/newkit_to_annalist_net.sh
    - [ ] src/newkit_to_conina_ubuntu.sh
    - [ ] Docker build scripts?
- [ ] Create new local installation and test again
- [ ] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [ ] Update front page link at annalist.net - copy `~annalist/uploads/pages/index.html` to `/var/www`
- [ ] Update demo installation on annalist.net; test
    - `killall python`
    - `pip uninstall annalist`
    - `pip install /var/www/software/Annalist-0.1.10.tar.gz --upgrade`
    - `annalist-manager runtests`
    - `. update-run-annalist.sh`
    - `cat annalist.out`
- [ ] Commit changes
- [ ] Upload to PyPI (see below)
- [ ] Merge final updates to master
- [ ] Test again on master branch
- [ ] Tag release on master branch
    - `git tag -a release-x.y.z`
- [ ] Push master branch, and tags
    - `git push --tags`
- [ ] On develop branch, bump version number again (back to odd value)
- [ ] Commit and push changes
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

