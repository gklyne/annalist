# Notes for software release preparation

## Summary of release tasks

- [ ] Feature freeze
- [ ] Test
- [ ] Demo deployment; test
- [ ] Documentation updates
- [ ] Demo screencast update
- [ ] Add TODO list to release notes, and reset
- [ ] Bump version and update history
- [ ] Update version number in scripts, documents, etc.
- [ ] Test again
- [ ] Post updated kit download
- [ ] Update front page link at annalist.net
- [ ] Upload to PyPI
- [ ] Final updates to master
- [ ] Test yet again
- [ ] Post announcement to Google Group, and elsewhere

## PyPI upload

Local:

    python setup.py build
    python setup.py sdist
    python setup.py install

Register with PyPI:

    python setup.py register

Upload to PyPI:

    python setup.py sdist upload

