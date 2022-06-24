#####################################
Setting up your first fastIoT Project
#####################################

There are some basics steps to follow to create your first project

************
Prerequisite
************

Following prerequisites are needed on a development machine:

 * Python Version 3.10.x installed (should work with Python 3.8+ as well though not tested)
 * Docker installed
 * `docker-compose` installed
 * Internet access for
   * Public Docker Repository _Docker Hub_
   * apt-Repository (for Linux Debian Stretch to install Packages in Docker Images)
   * pypi.python.org for python-library


**************
Setup Project
**************

    1. Create a new project directory
    2. Change to this directory, e.g. ``cd myproject``
    3. Create Python Virtual Environment: ``python3.10 -m venv venv``
    4. Activate VEnv: ``source venv/bin/activate``
    5. Install sam: ``pip install --no-binary=fastiot fastiot``
        * **Hint:** For easier debugging it is recommended to install fastiot using the ``--no-binary`` option. It can be
          dismissed and at a later point reinstalled adding the -I parameter to ignore previous installed versions and
          force a reinstall from source.
          However, we've noticed some issues where the PyCharm-IDE still uses the binary format after a reinstall and
          does not provide proper autocompletion. In such cases the easiest fix is to recreate the venv.

    6. Create basic directory structure for your project: ``fastiot.cli create new-project my_project_name``
        * For more options about creating projects see ``fastiot.cli --help``
    7. If working with PyCharm you have to mark the generated ``src`` directory as "Sources Root"
        For more information on PyCharm please refer to :ref:`label-setting-up-pycharm`
