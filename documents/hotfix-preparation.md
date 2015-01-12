# Notes for software hotfix preparation

## Summary of hotfix tasks

- [ ] Create new local hotfix branch from master branch
    - `git checkout -b hotfix-x.y.z<PATCH> master`
- [ ] Uninstall annalist
- [ ] Delete contents of build directory (ensure any old files are removed)
- [ ] Clean old .pyc files - `clean.sh`
- [ ] Fix bug, and add test cases
- [ ] Regenerate test data (e.g. `makeinitsitedata.sh` or `maketestsitedata.sh`)
- [ ] Local install
- [ ] Run test suite
- [ ] Update site data in local 'personal' installation
    - `annalist-manager initialize`
    - `annalist-manager updatesitedata`
- [ ] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [ ] Bump version to patch release and update history
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
- [ ] Demo deployment; test
- [ ] Update front page link at annalist.net
- [ ] Commit changes
- [ ] Upload to PyPI (see below)
- [ ] Merge hotfix updates to master
- [ ] Test again on master branch
- [ ] Tag release on master branch
    - `git tag -a release-x.y.z<PATCH>`
- [ ] Push master branch, and tags
    - `git push --tags`
- [ ] Merge hotfix updates to develop branch
    - [ ] resolve any conflicts
    - [ ] revert version number (back to odd value)
- [ ] Test again
- [ ] Delete hotfix branch
    - `git branch -d hotfix-x.y.z<PATCH>`
- [ ] Commit and push changes
- [ ] Post announcement to Google Group, and elsewhere


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

