#################
Building Services
#################

All Python FastIoT Services are built as docker images. Docker images are built via a Dockerfile. For all python services
a multistage Dockerfile template will be used. As of today it supports the stages debug and release mode.
In release mode all modules will be compiled via Nuitka and only the binary for the module will
be placed inside the image.

The template can be found within the :mod:`fastiot.cli` at :file:`src/fastiot/cli/templates/docker-compose.yaml.jinja`.
The template is used via the CLI and generates the Dockerfile in the build directory (typical :file:`build`) within
your project. You may use the command ``fiot build --dry`` to only generate the docker files and not start the
build immediately.

If you need your own Dockerfile just put a file called :file:`Dockerfile` in your service directory next to :file:`run.py`.
This will be used if found and replace the template based dockerfile.

For information how to add new python services, have a look at: :ref:`adding-services-label`
