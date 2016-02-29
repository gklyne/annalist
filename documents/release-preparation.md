# Notes for software release preparation

## Summary of release tasks

- [ ] Feature freeze
- [ ] Uninstall annalist (if installed): `pip uninstall annalist`
- [ ] Delete contents of build directory (remove old files) - python setup.py clean --all
- [ ] Clean old .pyc and temporary files
    - `git clean -nX` (trial run)
    - `git clean -fX` (do it)
- [ ] Local install
- [ ] Run test suite - `annalist-manager runtest`
- [ ] Update site data in local 'personal' installation
    - `annalist-manager updatesitedata`
    - `annalist-manager initialize`
- [ ] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [ ] Documentation and tutorial updates
- [ ] Demo screencast update
- [ ] Check all recent changes are committed (`git status`)

- [x] Create release preparation branch
    - git stash
    - git checkout -b release-prep-x.y.z develop
    - git stash pop
    - *NOTE* use a different name to that which will be used to tag the release
- [x] Add TODO list to release notes (edit out working notes)
- [x] Bump version to even value in `src/annalist_root/annalist/__init__.py`
- [x] Bump data compatibility version if new data is not compatible with older releases
- [x] Regenerate test data (e.g. `maketestsitedata.sh`, `makebibtestsitedata.sh` and `makeemptysitedata.sh`)
- [x] Reinstall and re-run test suite
- [x] Add release highlights description to release notes
- [x] Review issues list in GitHub (https://github.com/gklyne/annalist/issues)
- [x] Review roadmap (`documents/roadmap.md`)
- [ ] Update version number in scripts, documents, etc.
    - [x] Release notes
    - [x] documents/installing-annalist.md
    - [x] documents/roadmap.md
    - [x] documents/pages/index.html
    - [x] documents/tutorial/annalist-tutorial.adoc
    - [x] src/newkit_to_annalist_net.sh
    - [x] src/newkit_to_conina_ubuntu.sh
    - [x] Docker build scripts and makefiles
- [x] Create announcement text in `documents/release-notes/announce_0.1.*.md`
- [x] Check for new dependencies; update setup.py as needed.
    - copy kit to dev.annalist.net, install and test
        . newkit_to_annalist_net.sh
    - login to dev.annalist.net, then
        rm -rf anenv
        virtualenv anenv
        . anenv/bin/activate
        pip install software/Annalist-0.1.28.tar.gz
        annalist-manager runtests
    - Test new site creation:
        annalist-manager createsite
        annalist-manager initialize
        annalist-manager defaultadmin
        annalist-manager runserver &
        curl http://localhost:8000/annalist/site/ -v
- [x] Regenerate tutorial document
    - `asciidoctor -b html5 annalist-tutorial.adoc` or `. make-annalist-tutorial.sh` run in the `documents/tutorial` directory.
- [x] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [x] Update and test demo installation on annalist.net
    - ssh to annalist@annalist.net
    - `killall python`
    - `. anenv/bin/activate`
    - `pip uninstall annalist`
    - `pip install /var/www/software/Annalist-0.1.xx.tar.gz --upgrade`
    - `annalist-manager runtests`
    - `mv annalist_site/annalist.log archive/yyyymmdd-annalist.log`
    - `. update-run-annalist.sh`
    - `cat annalist.out`
- [x] Update front page link at annalist.net - copy `~annalist/uploads/pages/index.html` to `/var/www`
        cp ~annalist/uploads/pages/index.html /var/www
- [x] Update tutorial document at annalist.net
        cp ~annalist/uploads/documents/tutorial/* /var/www/documents/tutorial/
- [x] Check out demo system.
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
- [ ] Bump/check Zenodo DOI details:
    - On GitHub, create a new release
    - The rest should just happen.
    - The DOI in the badge should update
    - It may take a few minutes for the new DOI to resolve.
- [ ] On develop branch, bump version number again (back to odd value)
- [ ] Reset TODO list (remove entries moved to release notes, update version)
- [ ] Commit and push changes
- [ ] Delete release branch
    - `git branch -d release-prep-x.y.z`
- [ ] Regenerate test data (e.g. `maketestsitedata.sh`, `makebibtestsitedata.sh` and `makeemptysitedata.sh`), retest
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

The following sequence must be run on any system with docker installed (cf. ssh-dev-annalist.sh).  It assumes that the relevant version of Annalist has been installed and tested on the local system.

Use a well-connected Linux system for the following steps, and set the python virtual environment.

    # On dev.annalist.net:
    ANNALIST=~/github/gklyne/annalist
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

See [installing-annalist.md](installing-annalist.md) for details of how to run and test the resulting container.  Or just some combination of:

    docker ps
    docker pull gklyne/annalist_site
    docker pull gklyne/annalist
    docker run --detach --publish=8000:8000 --volumes-from=annalist_site     gklyne/annalist     annalist-manager runserver
    docker ps
    curl -v http://localhost:8000/annalist/
    curl -v http://localhost:8000/annalist/site/
    docker run --interactive --tty --rm     --volumes-from=annalist_site     gklyne/annalist bash
      # check out admin stripts, etc
    docker stop <container-id>
    docker ps

