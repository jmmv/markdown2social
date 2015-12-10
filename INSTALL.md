# Installation instructions

## For end users

To get started, simply use `pip` to download and install Markdown2Social along
all of its dependencies:

    pip install markdown2social

Alternatively, to build the tool from a source tree checked out from GitHub and
install it in the system location, do:

    ./setup.py install

For more information, see the standard Python's `distutils` usage instructions:

    https://docs.python.org/2/install/

## For developers

You can install Markdown2Social under an unprivileged tree for testing with:

    ./setup.py develop --user

Additionally, the command above will install symlinks to your source tree
instead of copies of your files, which means any changes to the code will
immediately show up in the installed copy of Markdown2Social.

To run regression tests:

    ./setup.py test
