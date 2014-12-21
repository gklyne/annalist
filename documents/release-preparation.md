# Notes for software release preparation

## Summary of release tasks

- [x] Feature freeze
- [x] Delete contents of build directory (ensure any old files are removed)
- [x] Clean old .pyc files - `clean.sh`
- [x] Regenerate test data (e.g. `makeinitsitedata.sh` or `maketestsitedata.sh`)
- [x] Local install
- [x] Run test suite
- [x] Update site data in local 'personal' installation
    - `annalist-manager initialize`
    - `annalist-manager updatesitedata`
- [x] Test 'personal' deployment in actual use
    - `annalist-manager runserver`
- [x] Demo deployment; test
- [x] Documentation updates
- [-] Demo screencast update
- [x] Add TODO list to release notes, and reset
- [x] Bump version to even value and update history
- [ ] Update version number in scripts, documents, etc.
    - [x] TODO
    - [x] Release notes
    - [x] documents/installing-annalist.md
    - [x] documents/release-notes/announce_0.1.*.md
    - [x] documents/roadmap.md
    - [x] documents/pages/index.html
    - [x] src/annalist_root/annalist/__init__.py
    - [x] src/newkit_to_annalist_net.sh
    - [x] src/newkit_to_conina_ubuntu.sh
- [x] Create new local installation and test again
- [x] Create and post updated kit download to annalist.net
    - use `src/newkit_to_annalist_net.sh`
- [x] Update front page link at annalist.net
- [ ] Commit changes
- [ ] Upload to PyPI (see below)
- [ ] Merge final updates to master
- [ ] Test again on master branch
- [ ] On develop branch, bump version number again (back to odd value)
- [ ] Commit changes
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

