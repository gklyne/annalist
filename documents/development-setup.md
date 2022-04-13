# development-setup.md

## Set up dev environment

@@TODO: check this

    python3 -m venv anenv3
    source anenv3/bin/activate
    python -m pip install --upgrade pip
    python -m pip install --upgrade certifi
    python -m pip install --upgrade setuptools
    python -m pip install --upgrade build
    python -m pip install --upgrade twine


## Get source

    git clone @@@@


## Install software from local source

From `src` directory; uses `setup.py` for requirements:

    pip install . 

@@TODO: switch to declarative configuration?


## Build software distributions

From `src` directory:

    python -m build

    twine check dist/Annalist-x.y.z*

    # twine upload dist/Annalist-x.y.z*

