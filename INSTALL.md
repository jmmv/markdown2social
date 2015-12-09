# Installation instructions

## For end users

To get started, simply run:

    ./setup.py install

This command will install markdown2social in the default system location
and download any necessary dependencies.

For more information, see the standard Python's `distutils` usage instructions:

    https://docs.python.org/2/install/

## For developers

You can install markdown2social under an unprivileged tree for testing with:

    ./setup.py develop --user

Additionally, the command above will install symlinks to your source tree
instead of copies of your files, which means any changes to the code will
immediately show up in the installed copy of markdown2social.

To run regression tests:

    ./setup.py test
