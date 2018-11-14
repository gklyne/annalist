This text removed from `installing-annalist.md`, and parked here in case it is later useful.

### Notes for installing and using virtualenv on Windows 7

**UPDATE**: after several hours of wrestling with obscure problems, I've given up trying to run the Annlist software on Windows.  In particular, the Windows file system appears to be particularly inconsistent in its behaviour, with bulk file delete and copy operations used by the test suite not performing reliably.  Since Annalist is highly dependent on reliable performance of the underlying file system, I have to conclude that it should not be expected to runb properly on Windows.  Maybe one day I'll try again, so I'll leave these notes here, but for now they serve little purpose..

On a fresh Windows install of Python, pip appears to be needed to install virtualenv;  see [How to install pip on windows?](http://stackoverflow.com/questions/4750806/).

After installing Python to its default location, `c:\Python27\`, the sequence I used was:

- download `get_pip.py`
- start a command shell with admin access. (From start menu, type `cmd` into the search box, then press CTRL+SHIFT+ENTER.)
- change to the directory where `getr_pip.py` was downloaded
- enter the command `python get_pip.py`.
- Finally, `C:\Python27\Scripts\pip.exe install virtualenv`.

Then, to use virtualenv to create a new Python virtual environment called `annenv`, start a normal (non-administrative) command shell, and enter:

    C:\Python27\Scripts\virtiualenv.exe annenv
    annenv\Scripts\activate

Notice that the command prompt changes to include the virtual environment name.  Now continue the installation procedure below from step 3, but noting that the command needed to run the Annalist manager utility is `annenv\Scripts\annalist-manager.exe` 
