# Notes for software release preparation

## Release x.y.z1/z2 checklist

- [ ] Feature freeze
- [ ] Check GitHub for security alerts; ensure requirements/common.txt and src/setup.py are up-to-date with secure package versions.
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
- [ ] Test collection installation; e.g.
    - `annalist-manager installcoll RDF_schema_defs --force`
    - `annalist-manager installcoll Annalist_schema --force`    
- [ ] Test migrations; e.g.
    - `annalist-manager migratecoll RDF_schema_defs`
    - `annalist-manager migratecoll Annalist_schema`
    - (check ~/annalist_site/annalist.log for errors/warnings)
- [ ] Test 'personal' deployment in actual use
    - `annalist-manager stopserver`
    - `annalist-manager runserver`
- [ ] Documentation and tutorial updates
- [ ] Demo screencast update
- [ ] Check all recent changes are committed (`git status`)
- [ ] Tag unstable release version on develop branch (e.g. "release-x.y.z1")
    - ```git tag -a release-`annalist-manager version` ```
    - For message:
        "Annalist release x.y.z1: (one-line summary)"
- [ ] Create release preparation branch
        git stash
        git checkout -b release-prep-x.y.z1 develop
        git stash pop
    - *NOTE* use a different name to that which will be used to tag the release
- [ ] Bump version to even value in `src/annalist_root/annalist/__init__.py`
- [ ] Bump data compatibility version if new data is not compatible with older releases
- [ ] Regenerate test data (e.g. `maketestsitedata.sh` and `makeemptysitedata.sh`)
- [ ] Reinstall and re-run test suite

- [ ] Add TODO list to release notes (edit out working notes)
- [ ] Add release highlights description to release notes
    - (create new release notes file if needed)
- [ ] Review issues list in GitHub (https://github.com/gklyne/annalist/issues)
- [ ] Review roadmap (`documents/roadmap.md`)
- [ ] Update version number in scripts, documents, etc.
    - [ ] Release notes
    - [ ] documents/installing-annalist.md
    - [ ] documents/roadmap.md
    - [ ] documents/pages/index.html
    - [ ] documents/tutorial/annalist-tutorial.adoc
    - [ ] Docker build scripts and makefiles
- [ ] Review and update GitHub project README.
- [ ] Create announcement text in `documents/release-notes/announce_x.y.z2.md`
- [ ] Regenerate tutorial document
    - `asciidoctor -b html5 annalist-tutorial.adoc` or `. make-annalist-tutorial.sh` run in the `documents/tutorial` directory.

- [ ] Test installation tools (and check for new dependencies; update setup.py as needed).
    - [ ] copy kit to dev.annalist.net, install and test
        . newkit_to_annalist_dev.sh
    - [ ] If live Annalist service is running, login to annalist.net as 'annalist', then
            source anenv3/bin/activate
            annalist-manager stop
        or `killall python` or `killall python3`
    - [ ] login to dev.annalist.net as 'annalist-dev', then
            rm -rf anenv3
            python3 -m venv anenv3
            source anenv3/bin/activate
            python -m pip install --upgrade pip
            python -m pip install --upgrade certifi
            python -m pip install --upgrade setuptools
            pip install uploads/Annalist-x.y.z2.tar.gz
            annalist-manager runtests
    - [ ] Test new site creation:
            annalist-manager createsite
            annalist-manager collectstatic
            annalist-manager initialize
            annalist-manager defaultadmin
            annalist-manager runserver
            curl http://localhost:8000/annalist/site/ -v
            annalist-manager stopserver
- [ ] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [ ] Set up to install Annalist in target system
    - [ ] ssh to gk-admin@annalist.net
    - [ ] check HTTPS proxy and Certbot setup (currently using `nginx`)
    - [ ] ssh to annalist@annalist.net, (or `su - annalist`)
    - NOTE: examples files in `src/annalist_root/annalist/data/config_examples/`
- [ ] Update and test demo installation on annalist.net
        . backup_annalist_site.sh
        . anenv3/bin/activate
        annalist-manager stop   #  or `killall python` or `killall python3`
        pip uninstall annalist
- [ ] Install new Annalist kit just uploaded (with `0.5.xx` changed to release number):
            pip install ~/software/Annalist-x.y.z2.tar.gz --upgrade
                # NOTE: this may fail with `pip` version 22.0.4 -- use `pip` version 21.3.1 to remove Django
            annalist-manager runtests
            . update-annalist-site.sh
            . update-run-annalist.sh
- [ ] Update front page at annalist.net (as root user):
            cp ~annalist/uploads/pages/index.html /var/www/annalist.net
            cp ~annalist/uploads/pages/css/style.css /var/www/annalist.net/css/
            cp ~annalist/uploads/pages/img/* /var/www/annalist.net/img/
- [ ] Update tutorial document at annalist.net
            cp -r ~annalist/uploads/tutorial/* /var/www/annalist.net/tutorial/
- [ ] Check out demo system at http://annalist.net/annalist/

- [ ] Commit changes ("Release x.y.z2")
- [ ] Upload to PyPI
        python -m build
        twine check dist/Annalist-x.y.z2*
        twine upload dist/Annalist-x.y.z2*
- [ ] Tag release on release branch
    - `git tag -ln` to check previous tags
    - `git tag -a release-x.y.z2`
    - For message:
        "Annalist release x.y.z2: (one-line summary)"
- [ ] Merge release branch to master
    - e.g.
        - `git checkout master`
        - `git merge release-prep-x.y.z1`
- [ ] Test again on master branch
- [ ] Push master branch, and tags
    - `git add ..`
    - `git commit -m "Master branch updated to Vx.y.z2"`
    - `git push`
    - `git push --tags`
- [ ] Merge release branch to develop
    - take care to ensure the branch is merged, not the tagged release
    - e.g.
        - `git checkout develop`
        - `git merge release-prep-x.y.z1`
- [ ] Bump/check Zenodo DOI details:
    - On GitHub, create a new release
        - release tag: `release-x.y.z2`
        - release title: (one-line summary)
        - release description: (1-paragraph description from release notes summary)
    - The rest should just happen.
        - Note: a new Zenodo URL is generated for the release.
    - The link in the DOI badge should display the new release from Zenodo.


## Set up next development cycle

- [ ] Update release-preparation.md with any process changes applied...
- [ ] On develop branch, bump version number again (back to odd value)
    - `annalist/src/annalistr_rooit/annalist/__init__.py`
- [ ] Reset TODO list (remove entries moved to release notes, update version)
- [ ] Regenerate test data (e.g. `maketestsitedata.sh` and `makeemptysitedata.sh` in `src/annalist_root`)
- [ ] Re-test (use python `manage.py test`)
- [ ] Commit and push changes
    - message: "Bump development branch release to x.y.z3"
- [ ] Delete release branch
    - `git branch -d release-prep-x.y.z2`

- [ ] Create Docker image, test (see below)
- [ ] Push docker image to DockerHub (see below)
- [ ] Post announcement to Google Group, Twitter and elsewhere
    - https://groups.google.com/forum/#!forum/annalist-discuss


## Build kit and PyPI upload

Local, run from `annalist/src` directory:

    python setup.py clean --all
    python -m build
    twine check dist/Annalist-x.y.z*
    pip install . 

Upload to PyPI:

    twine upload dist/Annalist-x.y.z*

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

