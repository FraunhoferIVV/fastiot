======================================================
Adapting the build system to your local infrastructure
======================================================

There are some environment variables you can set to have the CLI use more of your local infrastructure.
Those will be read out everytime running the CLI.

.. envvar:: FASTIOT_DOCKER_REGISTRY
Allows to set a custom (local) docker registry. You may include the port, e.g. ``my_registry:5000``. If the
build-command is triggered with ``--push`` this is also the registry to use.

.. envvar:: FASTIOT_DOCKER_REGISTRY_CACHE
If your registry supports caching or you have a seperate registry to store images, including intermediate images,
you can specify this here. See `Docker buildx documentation <https://docs.docker.com/engine/reference/commandline/buildx_build/#cache-from>` for more details.)
for more details about global caches.

.. envvar:: FASTIOT_EXTRA_PYPI
This allows you to use a local (or alternative) Python Package Index Server (PyPi) to host local Python packages.
It will be used whenever a container is built and the corresponding :file:`install.sh` is executed.

Besides that the CLI is designed in a way to be the single point for starting integration test dependencies, run tests,
build library and containers and upload them to the registry. This can easy setting up a CI-runner like Jenkins
significantly.