# Notes for software release preparation

## Release 0.5.17/18 checklist

- [x] Feature freeze
- [x] Check GitHub for security alerts; ensure requirements/common.txt and src/setup.py are up-to-date with secure package versions.
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
- [x] Test collection installation; e.g.
    - `annalist-manager installcoll RDF_schema_defs --force`
    - `annalist-manager installcoll Annalist_schema --force`    
- [x] Test migrations; e.g.
    - `annalist-manager migratecoll RDF_schema_defs`
    - `annalist-manager migratecoll Annalist_schema`
    - (check ~/annalist_site/annalist.log for errors/warnings)
- [x] Test 'personal' deployment in actual use
    - `annalist-manager stopserver`
    - `annalist-manager runserver`
- [-] Documentation and tutorial updates
- [-] Demo screencast update
- [x] Check all recent changes are committed (`git status`)
- [x] Tag unstable release version on develop branch (e.g. "release-0.1.37")
    - ```git tag -a release-`annalist-manager version` ```
    - For message:
        "Annalist release 0.5.17: (Drop Python 2 support; upgrade Django to latest; dependency security upgrades)"
- [x] Create release preparation branch
        git stash
        git checkout -b release-prep-0.5.17 develop
        git stash pop
    - *NOTE* use a different name to that which will be used to tag the release
- [x] Bump version to even value in `src/annalist_root/annalist/__init__.py`
- [x] Bump data compatibility version if new data is not compatible with older releases
- [x] Regenerate test data (e.g. `maketestsitedata.sh` and `makeemptysitedata.sh`)
- [x] Reinstall and re-run test suite

- [x] Add TODO list to release notes (edit out working notes)
- [x] Add release highlights description to release notes
    - (create new release notes file if needed)
- [x] Review issues list in GitHub (https://github.com/gklyne/annalist/issues)
- [x] Review roadmap (`documents/roadmap.md`)
- [x] Update version number in scripts, documents, etc.
    - [x] Release notes
    - [x] documents/installing-annalist.md
    - [x] documents/roadmap.md
    - [x] documents/pages/index.html
    - [x] documents/tutorial/annalist-tutorial.adoc
    - [x] Docker build scripts and makefiles
- [x] Review and update GitHub project README.
- [x] Create announcement text in `documents/release-notes/announce_0.5.*.md`
- [x] Regenerate tutorial document
    - `asciidoctor -b html5 annalist-tutorial.adoc` or `. make-annalist-tutorial.sh` run in the `documents/tutorial` directory.

- [x] Test installation tools (and check for new dependencies; update setup.py as needed).
    - [x] copy kit to dev.annalist.net, install and test
        . newkit_to_annalist_dev.sh
    - [x] If live Annalist service is running, login to annalist.net as 'annalist', then
        source anenv3/bin/activate
        annalist-manager stop
    or `killall python` or `killall python3`
    - [x] login to dev.annalist.net as 'annalist-dev', then
        rm -rf anenv3
        python3 -m venv anenv3
        source anenv3/bin/activate
        python -m pip install --upgrade pip
        python -m pip install --upgrade certifi
        python -m pip install --upgrade setuptools
        pip install uploads/Annalist-0.5.18.tar.gz
        annalist-manager runtests
    - [x] Test new site creation:
        annalist-manager createsite
        annalist-manager collectstatic
        annalist-manager initialize
        annalist-manager defaultadmin
        annalist-manager runserver
        curl http://localhost:8000/annalist/site/ -v
        annalist-manager stopserver
- [x] Create and post updated kit download and web pages to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [x] Set up to install Annalist in target system
    - [x] ssh to gk-admin@annalist.net
    - [x] check HTTPS proxy and Certbot setup (currently using `nginx`)
    - [x] ssh to annalist@annalist.net, (or `su - annalist`)
    - NOTE: examples files in `src/annalist_root/annalist/data/config_examples/`
- [x] Update and test demo installation on annalist.net
    - [x] `. backup_annalist_site.sh`
    - [x] `. anenv3/bin/activate`
    - [x] `annalist-manager stop` or `killall python` or `killall python3`
    - [x] `pip uninstall annalist`
- [x] Install new Annalist kit just uploaded (with `0.5.xx` changed to release number):
    - [x] `pip install ~/software/Annalist-0.5.18.tar.gz --upgrade`
        - NOTE: this may fail with `pip` version 22.0.4 -- use `pip` version 21.3.1 to remove Django
    - [x] `annalist-manager runtests`
    - [x] `. update-annalist-site.sh`
    - [x] `. update-run-annalist.sh`
- [x] Update front page at annalist.net (as root user):
        cp ~annalist/uploads/pages/index.html /var/www/annalist.net
        cp ~annalist/uploads/pages/css/style.css /var/www/annalist.net/css/
        cp ~annalist/uploads/pages/img/* /var/www/annalist.net/img/
- [x] Update tutorial document at annalist.net
        cp -r ~annalist/uploads/tutorial/* /var/www/annalist.net/tutorial/
- [x] Check out demo system at http://annalist.net/annalist/

- [x] Commit changes ("Release 0.5.18")
- [x] Upload to PyPI (`python setup.py sdist upload`)
        python -m build
        twine check dist/Annalist-0.5.18*
        twine upload dist/Annalist-0.5.18*
- [ ] Tag release on release branch
    - `git tag -ln` to check previous tags
    - `git tag -a release-0.5.18`
    - For message:
        "Annalist release 0.5.18: (Drop Python 2 support; upgrade Django to latest; dependency security upgrades)"
- [ ] Merge release branch to master
    - e.g.
        - `git checkout master`
        - `git merge release-prep-x.y.z`
- [ ] Test again on master branch
- [ ] Push master branch, and tags
    - `git add ..`
    - `git commit -m "Master branch updated to V0.5.18"`
    - `git push`
    - `git push --tags`
- [ ] Merge release branch to develop
    - take care to ensure the branch is merged, not the tagged release
    - e.g.
        - `git checkout develop`
        - `git merge release-prep-x.y.z`
- [ ] Bump/check Zenodo DOI details:
    - On GitHub, create a new release
        - release tag: `release-x.y.z`
        - release title: (one-line description text)
        - release description: 1-paragraph description from release notes summary
    - The rest should just happen.
        - Note: a new Zenodo URL is generated for the release.
    - The link in the DOI badge should display the new release from Zenodo.


## Set up next development cycle

- [ ] On develop branch, bump version number again (back to odd value)
- [ ] Reset TODO list (remove entries moved to release notes, update version)
- [ ] Regenerate test data (e.g. `maketestsitedata.sh` and `makeemptysitedata.sh`)
- [ ] Re-test
- [ ] Commit and push changes
    - message: "Bump development branch release to x.y.z"
- [ ] Delete release branch
    - `git branch -d release-prep-x.y.z`

- [ ] Create Docker image, test (see below)
- [ ] Push docker image to DockerHub (see below)
- [ ] Post announcement to Google Group, Twitter and elsewhere
    - https://groups.google.com/forum/#!forum/annalist-discuss


## Build kit and PyPI upload

Local:

    python setup.py clean --all
    python setup.py build
    python setup.py sdist
    python setup.py install

Upload to PyPI:

    python setup.py sdist upload

NOTE: upload now requires a recent version of setuptools to be installed; some older versions use a deprecated PyPi API.  To update, use some combination of these commands in the virtual environment:

    pip uninstall setuptools
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python
    pip install setuptools --upgrade
    easy_install --version

### Problems with old versions of software and TLS

On upgrading the version of Pythonto 2.7.14 in April 2018 I ran into a number of compatibility problems with loading python packages.  It appears that:

1. pip needs to be updated to use the latest version of TLS (1.3, I assume)
2. setuptools need to be updated.

On MacOS, I ended up using the following commands, after installing the latest version of Python2, and changing to the Annalist project base directory:

    rm -rf anenv
    virtualenv anenv -p python2.7
    source anenv/bin/activate
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    # Look for: "Successfully installed pip-9.0.3 wheel-0.31.0"
    pip install --upgrade setuptools
    # Note: installation reports success, then I got an error traceback, which seems
    #       to be caused by an access to the old (now removed) setuptools directory.
    #       It seems this error can be ignored.
    cd src
    python setup.py clean --all
    python setup.py build
    python setup.py install

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

