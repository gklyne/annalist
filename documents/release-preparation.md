# Notes for software release preparation

## Summary of release tasks

- [x] Feature freeze
- [x] Ensure default logging level is INFO (in `settings/common.py`, TRACE_FIELD_VALUE)
- [x] Uninstall annalist (if installed): `pip uninstall annalist`
- [x] Delete contents of build directory (remove old files) 
    - python setup.py clean --all
- [x] Clean old .pyc and temporary files
    - `git clean -nX` (trial run)
    - `git clean -fX` (do it)
- [x] Local install
- [x] Run test suite - `annalist-manager runtest`
- [x] Update site data in local 'personal' installation
    - `annalist-manager updatesitedata`
    - `annalist-manager initialize`
    - `annalist-manager updateadmin ...` (if needed)
- [x] Test collection installation; e.g.
    - `annalist-manager installcoll RDF_schema_defs`
    - `annalist-manager installcoll Annalist_schema`    
- [x] Test migrations; e.g.
    - `annalist-manager migratecoll RDF_schema_defs`
    - `annalist-manager migratecoll Annalist_schema`    
- [x] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [x] Documentation and tutorial updates
- [x] Demo screencast update
- [x] Check all recent changes are committed (`git status`)

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
- [x] Update version number in scripts, documents, etc.
    - [x] Release notes
    - [x] documents/installing-annalist.md
    - [x] documents/roadmap.md
    - [x] documents/pages/index.html
    - [x] documents/tutorial/annalist-tutorial.adoc
    - [x] src/newkit_to_annalist_net.sh
    - [x] src/newkit_to_annalist_dev.sh
    - [x] src/newkit_to_conina_ubuntu.sh
    - [x] Docker build scripts and makefiles
- [x] Create announcement text in `documents/release-notes/announce_0.1.*.md`
- [ ] Check for new dependencies; update setup.py as needed.
    - copy kit to dev.annalist.net, install and test (NOTE: may need VPN connection)
        . newkit_to_annalist_dev.sh
    - login to dev.annalist.net, then
        rm -rf anenv
        virtualenv anenv
        . anenv/bin/activate
        pip install software/Annalist-0.1.xx.tar.gz
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
- [x] Update front page link at annalist.net:
        cp ~annalist/uploads/pages/index.html /var/www
        cp ~annalist/uploads/pages/css/style.css /var/www/css/
- [x] Update tutorial document at annalist.net
        cp ~annalist/uploads/documents/tutorial/* /var/www/documents/tutorial/
- [x] Check out demo system.
- [x] Commit changes
- [x] Upload to PyPI (see below)
- [x] Tag release on release branch
    - `git tag -a release-x.y.z`
- [x] Merge release branch to master
    - e.g.
        - `git checkout master`
        - `git merge release-prep-x.y.z`
- [x] Test again on master branch
- [ ] Push master branch, and tags
    - `git add ..`
    - `git commit -m "Master branch updated to V0.1.30"`
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
- [ ] Regenerate test data (e.g. `maketestsitedata.sh`, `makebibtestsitedata.sh` and `makeemptysitedata.sh`), retest
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

Register with PyPI:

    python setup.py register

Upload to PyPI:

    python setup.py sdist upload


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

