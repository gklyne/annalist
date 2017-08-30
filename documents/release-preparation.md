# Notes for software release preparation

## Summary of release tasks

- [ ] Feature freeze
- [ ] Ensure default logging level is INFO (in `settings/common.py`, TRACE_FIELD_VALUE)
- [ ] Uninstall annalist (if installed): `pip uninstall annalist`
- [ ] Delete contents of build directory (remove old files) 
    - python setup.py clean --all
- [ ] Clean old .pyc and temporary files
    - `git clean -nX` (trial run)
    - `git clean -fX` (do it)
- [ ] Local install
- [ ] Run test suite - `annalist-manager runtest`
- [ ] Update site data in local 'personal' installation
    - `annalist-manager updatesitedata`
    - `annalist-manager initialize`
    - `annalist-manager updateadmin ...` (if needed)
- [ ] Test collection installation; e.g.
    - `annalist-manager installcoll RDF_schema_defs --force`
    - `annalist-manager installcoll Annalist_schema --force`    
- [ ] Test migrations; e.g.
    - `annalist-manager migratecoll RDF_schema_defs`
    - `annalist-manager migratecoll Annalist_schema`
    - (check ~/annalist_site/annalist.log for errors/warnings)
- [ ] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [ ] Documentation and tutorial updates
- [ ] Demo screencast update
- [ ] Check all recent changes are committed (`git status`)
- [ ] Tag unstable release version on develop branch (e.g. "release-0.1.37")
    - `git tag -a release-x.y.z`
    - For message:
        "Annalist release x.y.z: (one-line description of release)"

- [ ] Create release preparation branch
    - git stash
    - git checkout -b release-prep-x.y.z develop
    - git stash pop
    - *NOTE* use a different name to that which will be used to tag the release
- [ ] Add TODO list to release notes (edit out working notes)
- [ ] Bump version to even value in `src/annalist_root/annalist/__init__.py`
- [ ] Bump data compatibility version if new data is not compatible with older releases
- [ ] Regenerate test data (e.g. `maketestsitedata.sh` and `makeemptysitedata.sh`)
- [ ] Reinstall and re-run test suite
- [ ] Add release highlights description to release notes (create new release notes file if needed)
- [ ] Review issues list in GitHub (https://github.com/gklyne/annalist/issues)
- [ ] Review roadmap (`documents/roadmap.md`)
- [ ] Update version number in scripts, documents, etc.
    - [ ] Release notes
    - [ ] documents/installing-annalist.md
    - [ ] documents/roadmap.md
    - [ ] documents/pages/index.html
    - [ ] documents/tutorial/annalist-tutorial.adoc
    - [ ] src/newkit_to_annalist_net.sh
    - [ ] src/newkit_to_annalist_dev.sh
    - [ ] src/newkit_to_conina_ubuntu.sh
    - [ ] Docker build scripts and makefiles
- [ ] Create announcement text in `documents/release-notes/announce_0.5.*.md`
- [ ] Test installation tools (and check for new dependencies; update setup.py as needed).
    - [ ] copy kit to dev.annalist.net, install and test (NOTE: may need VPN connection)
        . newkit_to_annalist_dev.sh
    - [ ] login to dev.annalist.net as 'graham', then
        rm -rf anenv
        virtualenv anenv
        . anenv/bin/activate
        pip install software/Annalist-0.5.xx.tar.gz
        annalist-manager runtests
    - [ ] Test new site creation:
        annalist-manager createsite
        annalist-manager initialize
        annalist-manager defaultadmin
        annalist-manager runserver &
        curl http://localhost:8000/annalist/site/ -v
- [ ] Regenerate tutorial document
    - `asciidoctor -b html5 annalist-tutorial.adoc` or `. make-annalist-tutorial.sh` run in the `documents/tutorial` directory.
- [ ] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`

- [ ] Update and test demo installation on annalist.net
    - [ ] ssh to annalist@annalist.net
    - [ ] `. backup_annalist_site.sh`
    - [ ] `mv annalist_site_2015MMDD/ annalist_site_2017----`
    - [ ] `killall python`
    - [ ] `. anenv/bin/activate`
    - [ ] `pip uninstall annalist`
    - [ ] `pip install /var/www/software/Annalist-0.5.xx.tar.gz --upgrade`
    - [ ] `annalist-manager runtests`
    - [ ] `. update-annalist-site.sh`
    - [ ] `. update-run-annalist.sh`
    - [ ] `cat annalist.out`
- [ ] Update front page link at annalist.net:
        cp ~annalist/uploads/pages/index.html /var/www
        cp ~annalist/uploads/pages/css/style.css /var/www/css/
- [ ] Update tutorial document at annalist.net
        cp ~annalist/uploads/documents/tutorial/* /var/www/documents/tutorial/
- [ ] Check out demo system.

- [ ] Commit changes ("Preparing release x.y.z")
- [ ] Upload to PyPI (see below)
- [ ] Tag release on release branch
    - `git tag -a release-x.y.z`
    - For message:
        "Annalist release x.y.z: (one-line description of release)"
- [ ] Merge release branch to master
    - e.g.
        - `git checkout master`
        - `git merge release-prep-x.y.z`
- [ ] Test again on master branch
- [ ] Push master branch, and tags
    - `git add ..`
    - `git commit -m "Master branch updated to V0.1.36"`
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
        - Note: a new Zenodo URL is generated for the release.
    - The DOI in the badge should display the new release
    - It may take a few minutes for the new DOI to resolve.
- [ ] On develop branch, bump version number again (back to odd value)
- [ ] Reset TODO list (remove entries moved to release notes, update version)
- [ ] Regenerate test data (e.g. `maketestsitedata.sh` and `makeemptysitedata.sh`)
- [ ] Re-test
- [ ] Commit and push changes
- [ ] Delete release branch
    - `git branch -d release-prep-x.y.z`

- [ ] Create Docker image, test (see below)
- [ ] Push docker image to DockerHub (see below)
- [ ] Post announcement to Google Group, Twitter and elsewhere


## Build kit and PyPI upload

Local:

    python setup.py clean --all
    python setup.py build
    python setup.py sdist
    python setup.py install

Upload to PyPI:

    python setup.py sdist upload

NOTE: upload now requires a recent version of setuptools to be installed; some older versions use a deprecated PyPi API.  Python 2.7.3 on MacOS seems to provide an outdated version in a virtualenv.  To update, use some combination of these commands in the virtual environment:

    pip uninstall setuptools
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python
    pip install setuptools --upgrade
    easy_install --version


## Create docker images

The following sequence must be run on any system with docker installed (cf. ssh-dev-annalist.sh).  It assumes that the relevant version of Annalist has been installed and tested on the local system.

Use a well-connected Linux system for the following steps, and set the python virtual environment.

    # On dev.annalist.net:
    . anenv/bin/activate
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
    docker run --name=annalist_site --detach gklyne/annalist_site
    docker run --detach --publish=8000:8000 --volumes-from=annalist_site     gklyne/annalist     annalist-manager runserver
    docker ps
    curl -v http://localhost:8000/annalist/
    curl -v http://localhost:8000/annalist/site/
    docker run --interactive --tty --rm     --volumes-from=annalist_site     gklyne/annalist bash
      # check out admin scripts, etc
    docker stop <container-id>
    docker ps

Clean up old docker containers 
(ht https://twitter.com/jpetazzo/status/347431091415703552):

    docker ps -a | grep 'weeks ago' | awk '{print $1}' | xargs --no-run-if-empty docker rm
    docker ps -a | grep 'months ago' | awk '{print $1}' | xargs --no-run-if-empty docker rm

