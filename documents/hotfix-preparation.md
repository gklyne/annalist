# Notes for software hotfix preparation

## Summary of hotfix tasks

- [x] Create new local hotfix branch from master branch
    - `git checkout -b hotfix-x.y.z<PATCH> master`
- [x] Uninstall annalist
- [x] Delete contents of build directory (ensure any old files are removed)
- [x] Clean old .pyc files - `clean.sh`
- [x] Fix bug, and add test cases
- [x] Regenerate test data (e.g. `makeinitsitedata.sh` or `maketestsitedata.sh`)
- [x] Local install
- [x] Run test suite
- [x] Update site data in local 'personal' installation
    - `annalist-manager initialize`
    - `annalist-manager updatesitedata`
- [x] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [x] Bump version to patch release and update history
- [ ] Update version number in scripts, documents, etc.
    - [x] Release notes
    - [ ] documents/installing-annalist.md
    - [ ] documents/release-notes/announce_0.1.*.md
    - [x] documents/roadmap.md
    - [x] documents/pages/index.html
    - [x] src/annalist_root/annalist/__init__.py
    - [x] src/newkit_to_annalist_net.sh
    - [x] src/newkit_to_conina_ubuntu.sh
- [x] Create and post updated kit download to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [x] Demo deployment; test
- [x] Update front page link at annalist.net
- [x] Commit changes
- [x] Upload to PyPI (see below)
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

    python setup.py build
    python setup.py sdist
    python setup.py install

Register with PyPI:

    python setup.py register

Upload to PyPI:

    python setup.py sdist upload

