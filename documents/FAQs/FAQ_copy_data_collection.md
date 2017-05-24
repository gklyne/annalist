## How can I copy collections between Analist sites?

Annalist data collections are currently (2017-05) stored natively as a set of JSON-LD files, along with any media attachmemnts, on the Annalist server host system.  The file contents are system-independent and may be copied from one Analist installation to another.

Any inherited collections must be separately copied or installed on the target system, using the same collection name.

The files are probably most easily copied as a ZIP or TAR archive.  Alternatively a shared file system, USB stick or file transfer utility such as `scp` can be used.

A technique that I use employs `git` and [GitHub](https://github.com/).

### Save a collection to GitHub

To save collection data to GitHub (this requires shell login access to the server host system, a GitHub account and a suitably configured git instance on the Annalist server system):

1.  Log in to GitHub and create a new empty collection (I try to use the same name as the Annalist collection, but this isn't a requirement).  Make a note of the collection URL.

2.  Log in tio a shell account on the Annalist server system, and go to the directory containing the collection to be saved; e.g.:

        cd ~/annalist_site/c/my_collection/

3.  Clone the new repository from GitHub to the current directory; e.g.

        git init
        git add .
        git commit -m "my_collection initial commit"
        git remote add origin git@github.com:gklyne/my_collection.git
        git push -u origin master

    NOTE: the string `git@github.com:gklyne/my_collection.git` should be replaced by the repository URL created in step 1.

4. Any subsequent updates to the collection can be saved as a new version using the following commands:

        git add .
        git commit -m "summary of updates"
        git push

### Restore a collection from GitHub

To restore collection data from GitHub (this requires shell login access to the target server host system, a GitHub account and a suitably configured git instance on the Annalist server system):

1.  Log in to a shell account on the Annalist server system, and go to the Annalist collections home directory; e.g.:

        cd ~/annalist_site/c/

2.  Install any common Annalist installable collections used; e.g.

        annalist-manager installcollecton Resource_defs

    Note: this requires the installed Annalist python environment to be activated; e.g.

        source anenv/bin/activate

    (See the [Installing and setting up Annalist](../documents/installing-annalist.md) for more details.)

3.  Clone the data from the git repository; e.g.

        git clone git@github.com:gklyne/my_collection.git

    where "git@github.com:gklyne/my_collection.git" is replaced with the GitHub repository URL noted when the repository was created.

At this point, if you browse to the Analist home page, the new collection should be listed.

