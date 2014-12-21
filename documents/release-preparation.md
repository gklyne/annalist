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
- [ ] Create new local installation and test again
- [ ] Create and post updated kit download to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [ ] Update front page link at annalist.net
- [ ] Commit changes
- [ ] Upload to PyPI (see below)
- [ ] Merge final updates to master
- [ ] Test again on master branch
- [ ] Push master branch
- [ ] On develop branch, bump version number again (back to odd value)
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

