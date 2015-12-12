# Notes for software hotfix preparation

## Summary of hotfix tasks

- [ ] Create new local hotfix branch from master branch
    - `git checkout -b hotfix-x.y.z<PATCH> master`
- [ ] Uninstall annalist
- [ ] Delete contents of build directory (ensure any old files are removed)
- [ ] Clean old .pyc files - `clean.sh`
- [ ] Fix bug, and add test cases
- [ ] Regenerate test data (e.g. `maketestsitedata.sh`, `makebibtestsitedata.sh` and `makeemptysitedata.sh`)
- [ ] Local install
- [ ] Run test suite
- [ ] Update site data in local 'personal' installation
    - `annalist-manager initialize`
    - `annalist-manager updatesitedata`
- [ ] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [ ] Bump version to patch release and update release notes history
    - `src/annalist_root/annalist/__init__.py`
- [ ] Update version number in scripts, documents, etc.
    - [ ] Release notes
    - [ ] documents/release-notes/announce_0.1.*.md
    - [ ] documents/roadmap.md
    - [ ] documents/pages/index.html
    - [ ] src/newkit_to_annalist_net.sh
    - [ ] src/newkit_to_conina_ubuntu.sh
- [ ] Create and post updated kit download to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [ ] Test in deployment environment where problem seen?
- [ ] Deploy updated kit on annalist.net
    - ssh to annalist@annalist.net
    - `killall python`
    - `. anenv/bin/activate`
    - `pip uninstall annalist`
    - `pip install /var/www/software/Annalist-0.1.xx.tar.gz --upgrade`
    - `annalist-manager runtests`
    - `. update-run-annalist.sh`
    - `cat annalist.out`
- [ ] Update front page link at annalist.net 
    - copy `~annalist/uploads/pages/index.html` to `/var/www`
        cp ~annalist/uploads/pages/index.html /var/www
- [ ] Commit changes
- [ ] Upload to PyPI (see below)
- [ ] Tag release on hotfix branch
    - `git tag -a release-x.y.z<PATCH>`
- [ ] Merge hotfix updates to master
- [ ] Test again on master branch
- [ ] Push master branch, and tags
    - `git push --tags`
- [ ] Merge hotfix updates to develop branch
    - [ ] resolve any conflicts
    - [ ] revert version number (back to odd value)
- [ ] Regenerate test data (e.g. `maketestsitedata.sh`, `makebibtestsitedata.sh` and `makeemptysitedata.sh`)
- [ ] Test again
- [ ] Commit and push changes
- [ ] Post announcement to Google Group, and elsewhere
- [ ] Delete hotfix branch 
    - (do this last when all the changes have been checked out.  It further changes are needed, do them on the hotfix branch and re-merge to master and develop)
    - `git branch -d hotfix-x.y.z<PATCH>`


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

