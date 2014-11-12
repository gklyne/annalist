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
- [ ] Upload to PyPI (see below)
- [ ] Final updates to master
- [ ] Test yet again
- [ ] Post announcement to Google Group, and elsewhere
- [ ] Bump version number again (back to odd value)

## Build kit and PyPI upload

Local:

    python setup.py build
    python setup.py sdist
    python setup.py install

Register with PyPI:

    python setup.py register

Upload to PyPI:

    python setup.py sdist upload

