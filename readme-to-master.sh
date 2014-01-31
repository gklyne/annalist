#!/usr/bin/env bash
#
# Transfer README.md file in develop branch to master branch

if [[ "$1" == "" ]]; then

    echo "No commit message provided"
    exit 1

fi

MESSAGE=${1:-README updated from develop branch}

if [ -f README.md ]; then

    if git checkout master; then

        git checkout develop README.md
        git commit -m "$MESSAGE"
        git checkout develop    

    else

        echo "git checkout problem (uncommitted files?) - aborting"


    fi

else

    echo "no README.md file (wrong dirtectory?) - aborting"

fi

# End.
