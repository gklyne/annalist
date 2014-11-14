# Notes for software release preparation

## Summary of release tasks

- [ ] Feature freeze
- [ ] Test
- [ ] Demo deployment; test
- [ ] Documentation updates
- [ ] Demo screencast update
- [ ] Add TODO list to release notes, and reset
- [ ] Bump version to even value and update history
- [ ] Update version number in scripts, documents, etc.
- [ ] Test again
- [ ] Create and post updated kit download to annalist.net
- [ ] Update front page link at annalist.net
- [ ] Upload to PyPI (see below)
- [ ] Final updates to master
- [ ] Test yet again
- [ ] On develop branch, bump version number again (back to odd value)
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

