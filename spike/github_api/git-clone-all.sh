#!/usr/bin/env bash
#
# Clone all github repositories for named user
#
# See also: http://xkcd.com/974/
#

if [ "$1" == "" ]; then
    echo "Usage: . git-clone-all.sh <userid>"
    echo
    echo "Clones all github repositories for user <userid> into a siubdirectory of the same name."
    return 1
fi

USERID=${1-gklyne}
echo "Cloning repositories for user $USERID"

python get_github_repos.py $USERID "echo git clone %(git_url)s && git clone %(git_url)s" > $USERID/get_github_repos.tmp
mkdir $USERID
pushd $USERID
source get_github_repos.tmp
popd

# End

