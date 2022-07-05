.. _label-cli-intro:

################################################################
Building Docker Images and Generating config files – fastiot.cli
################################################################

The ``fastiot.cli`` is your best tool for managing the build process of any fastIoT-project. It takes care of building docker
images using files stored in :file:`build`, generating configs from deployments under :file:`generated`, generating a :file:`generated.py` file for testing
purposes and manage local deployments. See :ref:`project_structure` for more information about the general structure of a FastIoT project.

*****************************
Setting environment variables
*****************************

You need to specify the environment variables :envvar:`FASTIOT_EXTRA_PYPI` and :envvar:`FASTIOT_DOCKER_REGISTRY` before running ``fastiot.cli``. You can do
so by calling following commands if you are an ivv-dd employee and not using a centrally administrated Linux system within Fraunhofer IVV.
On these systems this is configured already::

  export FASTIOT_EXTRA_PYPI=pypi.dev.ivv-dd.fhg.de
  export FASTIOT_DOCKER_REGISTRY=docker.dev.ivv-dd.fhg.de
  export FASTIOT_DOCKER_REGISTRY_CACHE=docker.dev.ivv-dd.fhg.de:5005

You can also put these lines in a Bash Script in a file inside :file:`/etc/profile.d/`.
This should work on pretty much any Linux.

Or by passing it before each call like:
``FASTIOT_EXTRA_PYPI=pypi.dev.ivv-dd.fhg.de FASTIOT_DOCKER_REGISTRY=docker.dev.ivv-dd.fhg.de:5000 fastiot.cli <args>``

The environment variable :envvar:`FASTIOT_EXTRA_PYPI` specifies the pypi repository where additional libraries can be pulled. The
environment variable :envvar:`FASTIOT_DOCKER_REGISTRY` is optional, but recommended to always tag built images with the docker
registry and generated configs also with the docker registry as image name.

*********************
Executing fastiot.cli
*********************

You can execute it like ``fastiot.cli <args>``. Call ``fastiot.cli -h`` for additional help.

Docker Images and custom docker-compose files based on your sam-compose.yaml are built via ``fastiot.cli build`` and
``fastiot.cli config``, respectively. Before running your first project you always need to build the docker-compose
file, thus you need to run ``fastiot.cli config`` at least once.

To compile modules, add flag ``fastiot.cli build --mode=release``. Per default no modules will be compiled and will be
run with python interpreter.



*******************************
Some important additional notes
*******************************

The generated files will be put into :file:`generated/your_project`
Using this generated :file:`docker-compose.yaml` you can start modules and services like the nats broker or the database.
For more information about starting your module locally and running services from within docker refer to the next
tutorial :ref:`label-setting-up-pycharm`
