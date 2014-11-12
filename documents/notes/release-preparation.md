# Notes for software release preparation

## Summary of release tasks

- [x] Feature freeze
- [x] Test
- [x] Demo deployment; test
- [x] Documentation updates
- [x] Demo screencast update
- [x] Add TODO list to release notes, and reset
- [x] Bump version to even value and update history
- [x] Update version number in scripts, documents, etc.
- [x] Test again
- [x] Create and post updated kit download to annalist.net
- [x] Update front page link at annalist.net
- [x] Upload to PyPI (see below)
- [x] Final updates to master
- [x] Test yet again
- [x] On develop branch, bump version number again (back to odd value)
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

