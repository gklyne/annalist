## Background

As a first step to using "gitflow" branching structures (http://nvie.com/posts/a-successful-git-branching-model/)
a "develop" branch has been created.  In due course, the "master" branch should only ever contain production code
that has been published to PyPI.

I have not yet created branches for releases or feature development
I'm taking a view that these can be created as required.
Some developments may take place on a local branch and be pushed straight back to "develop".


## Some git incantations ##

See: http://nvie.com/posts/a-successful-git-branching-model/

Some content in this file has been adapted from that note.


### Create the develop branch ###

See: http://www.linux-pages.com/2011/05/how-to-create-a-brand-new-git-tracking-branch-from-scratch/ 

    git push origin master:develop
    git branch --track develop origin/develop

I found that pulling to an existing github repository did not set the tracking status for the new develop branch: I also had to use the following command suggested by git to pull changes on the new develop branch:

    git branch --set-upstream develop origin/develop

To delete the remote branch:

    $ git push origin --delete <branchName>


### Creating a feature branch ###

When starting work on a new feature, branch off from the develop branch.

    $ git checkout -b myfeature develop
    Switched to a new branch "myfeature"

Also:

    $ git push origin HEAD

Pushes to same-name branch at origin repo


### Incorporating a finished feature on develop ###

Finished features may be merged into the develop branch definitely add them to the upcoming release:

    $ git checkout develop
    Switched to branch 'develop'
    $ git merge --no-ff myfeature
    Updating ea1b82a..05e9557
    (Summary of changes)
    $ git branch -d myfeature
    Deleted branch myfeature (was 05e9557).
    $ git push origin develop

The --no-ff flag causes the merge to always create a new commit object, even if the merge could be performed with a fast-forward.


### Release branches ###

May branch off from: develop 
Must merge back into: develop and master 
Branch naming convention: release-*

Creating a release branch

    $ git checkout -b release-1.2 develop
    Switched to a new branch "release-1.2"
    $ ./bump-version.sh 1.2
    Files modified successfully, version bumped to 1.2.
    $ git commit -a -m "Bumped version number to 1.2"
    [release-1.2 74d9424] Bumped version number to 1.2
    1 files changed, 1 insertions(+), 1 deletions(-)

Finishing a release branch

    $ git checkout master
    Switched to branch 'master'
    $ git merge --no-ff release-1.2
    Merge made by recursive.
    (Summary of changes)
    $ git tag -a 1.2

    $ git checkout develop
    Switched to branch 'develop'
    $ git merge --no-ff release-1.2
    Merge made by recursive.
    (Summary of changes)

    $ git branch -d release-1.2
    Deleted branch release-1.2 (was ff452fe).

If the release branch was pushed to a remote repository as work-in-progress, also do:

    $ git push origin --delete release-1.2
    To git@github.com:gklyne/annalist.git
     - [deleted]         release-1.2


## Recovery actions

### Undo last commit

See: http://stackoverflow.com/questions/927358/undo-last-git-commit):

    git reset --soft HEAD^

### Transfer uncommitted changes to new branch

    git stash
    git checkout -b <branch>
    git stash pop


## Others

List all commits on branch b1 that are not also on branch b2:

    git log b1 ^b2 --no-merges


## More incantations

* https://github.com/blog/2019-how-to-undo-almost-anything-with-git
