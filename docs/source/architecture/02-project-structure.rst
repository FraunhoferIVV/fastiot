.. _project_structure:
=================
Project structure
=================

As FastIoT is considered a FrameWork certain directories and files are expected to be always at the same location.
For a new project this should usually be handled using the CLI (s. :ref:`first_project_setup` for more details).

``├── configure.py``  => This file sets up your project and defines where to find tests, library, … (Data Model: :class:`fastiot.cli.model.project.ProjectConfig`)

``├── deployments``

``│   ├── my_deployment``  => A deployment configuration to configure a list of services running on a (remote) system

``|   │   ├── .env`` => Environment variables

``│   │   ├── deployment.yaml`` => Deployment configuration (data model :class:`fastiot.cli.model.deployment.DeploymentConfig`)

``│   │   └── dev-overwrite.env`` => Environment variables to be overwritten for local tests

``│   └── integration_test``  => An deployment to be started on the CI runner

``│       └── […]``

``├── install.sh``  => Script to be started within the container to install packages, …

``├── Jenkinsfile`` => File for the CI runner, if needed

``├── README.md``  => It’s always nice to have a Readme

``├── requirements.txt``  => Python Packages to be installed in your venv and in all containers

``├── setup.py``  => If you want to build a library to be installed by other projects this is needed, use command :func:`fastiot.cli.commands.build_lib.build_lib`

``├── src``  => All your code belongs in heere

``│   ├── my_lib`` => The library

``│       └── […]`` => Some library code to be used by all services

``│   ├── my_services``

``│   │   ├── a_service``

``│   │   │   ├── __init__.py``

``│   │   │   ├── my_service.py``  => A file containing your actual service, this file will be obfuscated

``│   │   │   ├── manifest.yaml``  => A manifest describing your service (ports, mounts, …) (data model :class:`fastiot.cli.model.manifest.ServiceManifest`)

``│   │   │   └── run.py`` => This is the entry point used by docker for your service not to be obfuscated when building using :func:`fastiot.cli.commands.build.build`

``│   │   ├── […]``  => More services as you like

``│   ├── […]``  => More packages with services if you like

``│   └── my_tests``  => Put any tests files here and configure the package accordingly in your :file:`configure.py`, may be started using the :func:`fastiot.cli.commands.run.run_unittests` command.

