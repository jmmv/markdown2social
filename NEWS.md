Major changes between releases
==============================


Changes in version 0.4
----------------------

**STILL UNDER DEVELOPMENT; NOT RELEASED YET.**

* Moved list of dependencies to a requirements.txt file to simplify the
  installation of this package.


Changes in version 0.3
----------------------

**Released on January 14th, 2016.**

* Issue 2: Added a manual page.

* Added support for a configuration file.  The default is to load
  `~/.config/markdown2social.conf` if it exists, and the path can be
  overridden via the `--config_file` flag.

* Added support to specify a set of "replacements" to apply to the post
  text after conversion.  This is useful, for example, to automatically
  turn bare references to external systems into links.


Changes in version 0.2
----------------------

**Released on December 11th, 2015.**

* Migrated `setup.py` from `setuptools` to `distutils` so that the package
  documentation can be properly installed.  As a bonus, this cuts down a
  dependency.

* Fixed contents of the sdist: added missing documentation and `testdata`
  files.  Ah, the obvious mistakes one makes when publishing a Python
  package for the first time...


Changes in version 0.1
----------------------

**Released on December 10th, 2015.**

* First public release.
