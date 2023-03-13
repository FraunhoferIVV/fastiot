.. _tut-dependencies:

######################
Managing dependencies
######################

Managing your dependencies is crucial for your project.

The basic recommendations for Python (and other languages) are the following:
  * Keep the dependencies to your library as open as possible, to avoid the "dependency hell" for others importing your
    library. If you tie your versions very tight, other projects may run in trouble resolving all tight dependencies.
  * Fix the versions you are using for your builds. This will result in reproducible and thus stable builds.

FastIoT will help you to keep track of both if you follow the conventions:

Loose requirements in library
-----------------------------

Add your requirements loosely to :file:`pyproject.toml`. When setting up a new project this file will be automatically
created. For older projects you may use the command ``fiot create pyproject-toml``. This command will also use the
requirements already specified in the directory :file:`requirements` and add it to your :file:`pyproject.toml`.

**Attention:** Do not change your :file:`requirements.txt` to manage dependencies.

Fixed dependencies for builds
-----------------------------

Use the command ``fiot config`` to create a :file:`requirements.txt` with fixed requirements matching the current setup
at the time run. If you have specified additional requirements separate files will be created in the directory
:file:`requirements`. Already fixed versions will not be changed. You may consult the pip-tools homepage at
https://github.com/jazzband/pip-tools/ to get further information on the pip-compile command.

To upgrade to the latest packages use the command ``fiot config --update-requirements``. This will check if there are
updated versions of packages matching your requirements specified in :file:`pyproject.toml`. Don’t forget to test your
code afterwards and add the changed files to git!

Additional requirements / Optional dependencies
-----------------------------------------------

If you have any optional dependencies needed e.g. only for one container or in special use cases of your library you may
define those in your :file:`pyproject.toml`. See the official documentation at
https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#optional-dependencies for more information
on this topic.

.. code-block:: toml
   :caption: Example of adding additional requirements to your project:

   [project.optional-dependencies]
   my_addition = [
       "some-lib>=1,<2",
       "another lib",
   ]

Within FastIoT you can use the optional dependencies in your :ref:`tut-manifest` with
the attribute name :attr:`fastiot.cli.model.manifest.ServiceManifest.additional_requirements`