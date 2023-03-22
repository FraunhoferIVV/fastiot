.. _first_project_setup:
#####################################
Setting up your first FastIoT Project
#####################################

There are some basics steps to follow to create your first project

************
Prerequisite
************

Following prerequisites are needed on a development machine:

* Python Version 3.10.x installed (should work with Python 3.9 as well though not tested)
* Access to the command line
* We recommend PyCharm as IDE, though various others should work as well.


**************
Setup Project
**************

1. Create a new project directory
2. Change to this directory, e.g. ``cd myproject``
3. Create Python Virtual Environment: ``python3.10 -m venv venv``
4. Activate VEnv: ``source venv/bin/activate``
5. Install FastIoT: ``pip install fastiot``
6. Create basic directory structure for your project: ``fiot create new-project my_project_name``
     * For more options about creating projects see ``fiot create new-project --help``
7. Create a first service if you want to: ``fiot create new-service a_service``
8. Generate some configuration files with ``fiot config``
9. If working with PyCharm you have to Mark the generated ``src`` directory as "Sources Root".
     * For more information on PyCharm please refer to :ref:`label-setting-up-pycharm`
