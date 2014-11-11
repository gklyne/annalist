# Notes for software release preparation

## Summary of release tasks

- [x] Feature freeze
- [x] Test
- [ ] Demo deployment; test
- [x] Documentation updates
- [x] Demo screencast update
- [x] Add TODO list to release notes, and reset
- [ ] Bump version to even value and update history
- [ ] Update version number in scripts, documents, etc.
- [ ] Test again
- [ ] Post updated kit download
- [ ] Update front page link at annalist.net
- [ ] Upload to PyPI (see below)
- [ ] Final updates to master
- [ ] Test yet again
- [ ] Post announcement to Google Group, and elsewhere
- [ ] Bump version number again (back to odd value)

## PyPI upload

Local:

    python setup.py build
    python setup.py sdist
    python setup.py install

Register with PyPI:

    python setup.py register

Upload to PyPI:

    python setup.py sdist upload

