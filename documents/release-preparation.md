# Notes for software release preparation

## Summary of release tasks

- [x] Feature freeze
- [x] Uninstall annalist (if installed): `pip uninstall annalist`
- [x] Delete contents of build directory (remove old files) - python setup.py clean --all
- [x] Clean old .pyc and temporary files
    - `git clean -nX` (trial run)
    - `git clean -fX` (do it)
- [x] Local install
- [x] Run test suite - `annalist-manager runtest`
- [x] Update site data in local 'personal' installation
    - `annalist-manager updatesitedata`
    - `annalist-manager initialize`
- [x] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [x] Documentation and tutorial updates
- [x] Demo screencast update
- [ ] Check all recent changes are committed (`git status`)

- [ ] Create release preparation branch
    - git stash
    - git checkout -b release-prep-x.y.z develop
    - git stash pop
    - *NOTE* use a different name to that which will be used to tag the release
- [ ] Add TODO list to release notes (edit out working notes)
- [ ] Bump version to even value in `src/annalist_root/annalist/__init__.py`
- [ ] Bump data compatibility version if new data is not compatible with older releases
- [ ] Regenerate test data (e.g. `maketestsitedata.sh`, `makebibtestsitedata.sh` and `makeemptysitedata.sh`)
- [ ] Reinstall and re-run test suite
- [ ] Add release highlights description to release notes
- [ ] Review issues list in GitHub (https://github.com/gklyne/annalist/issues)
- [ ] Review roadmap (`documents/roadmap.md`)
- [ ] Update version number in scripts, documents, etc.
    - [ ] Release notes
    - [ ] documents/installing-annalist.md
    - [ ] documents/roadmap.md
    - [ ] documents/pages/index.html
    - [ ] documents/tutorial/annalist-tutorial.adoc
    - [ ] src/newkit_to_annalist_net.sh
    - [ ] src/newkit_to_conina_ubuntu.sh
    - [ ] Docker build scripts and makefiles
- [ ] Create announcement text in `documents/release-notes/announce_0.1.*.md`
- [ ] Check for new dependencies; update setup.py as needed.
- [ ] Regenerate tutorial document
    - `asciidoctor -b html5 annalist-tutorial.adoc` or `. make-annalist-tutorial.sh` run in the `documents/tutorial` directory.
- [ ] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [ ] Update and test demo installation on annalist.net
    - ssh to annalist@annalist.net
    - `killall python`
    - `. anenv/bin/activate`
    - `pip uninstall annalist`
    - `pip install /var/www/software/Annalist-0.1.xx.tar.gz --upgrade`
    - `annalist-manager runtests`
    - `. update-run-annalist.sh`
    - `cat annalist.out`
- [ ] Update front page link at annalist.net - copy `~annalist/uploads/pages/index.html` to `/var/www`
        cp ~annalist/uploads/pages/index.html /var/www
- [ ] Update tutorial document at annalist.net
        cp ~annalist/uploads/documents/tutorial/* /var/www/documents/tutorial/
- [ ] Commit changes
- [ ] Upload to PyPI (see below)
- [ ] Tag release on release branch
    - `git tag -a release-x.y.z`
- [ ] Merge release branch to master
    - e.g.
        - `git checkout master`
        - `git merge release-prep-x.y.z`
- [ ] Test again on master branch
- [ ] Push master branch, and tags
    - `git add ..`
    - `git commit -m "Master branch updated to Vx.y.z"`
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
- [ ] Regenerate test data (e.g. `maketestsitedata.sh`, `makebibtestsitedata.sh` and `makeemptysitedata.sh`), retest
- [ ] Commit and push changes

- [ ] Post announcement to Google Group, Twitter and elsewhere
- [ ] Create Docker image, test (see below)
- [ ] Push docker image to DockerHub (see below)


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

    # On dev.annalist.net:
    # ANNALIST=~/github/gklyne/annalist
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

