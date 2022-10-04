.. _deployment_yaml:

##########################################
Deployment configuration - deployment.yaml
##########################################

Configuration is done via :file:`deployment.yaml` file, the according data model can be found at
:class:`fastiot.cli.model.deployment.DeploymentConfig`, where you will always find the latest an in-depth documentation.
Here we will provide a short description of the core concepts. A useful starting point is automatically created when using
``fiot create new-project`` to create a new project.

- name: A meaningful name for the deployment.
- services: Dictionary of FastIoT Services (:class:`fastiot.cli.model.deployment.ServiceConfig`) within *and* from other projects.
- infrastructure-services: Dictionary with external services defined in :mod:`fastiot.cli.common.infrastructure_services`
  or created by yourself (s. :ref:`tut-custom_infrastructure_services`)
- docker-registry: Specify a docker registry to be used as base for the project
- tag: Specify a docker registry tag; per default "latest"
- config-dir: Specify a configuration directory which is mounted inside the service at '/etc/fastiot'. See also :envvar:`FASTIOT_CONFIG_DIR`
- deployment-target: A configuration based on :class:`fastiot.cli.model.deployment.DeploymentTargetSetup` for easy
  rollout of the project using Ansible.

Image Names and Services
========================

By default the image name will be constructed using the configured Docker-Registry (either in the file or using :envvar:`FASTIOT_DOCKER_REGISTRY`),
the project namespace from your :file:`configure.py`, the service and name and a tag: ``REGISTRY/namespace/image_name:tag``.

This can either be configured global or per service using an :class:`fastiot.cli.model.deployment.ServiceConfig`.

You can define the same service multiple times. In this case you need to use different names and thus the image-name
cannot be guessed correctly and you need to define it manually using :class:`fastiot.cli.model.deployment.ServiceConfig`.

Environment Variables
=====================

Environment variables are configured with a file called :file:`.env` in the deployment configuration.
Each service can have an empty value (which will default good defaults) but can also be configured with a
:class:`fastiot.cli.model.deployment.ServiceConfig`.

Short Example
=============

.. code-block:: yaml

  services:
    my_service:  # Will use the my_service with defaults, global .env-Vars from file .env
    my_service_with_extras:  # Using the same image a second time, but with additional settings
      image: my_project/my_service  # Setting the image name is a must!
      tag: 0.9
      environment:
        MY_SPECIAL_VAR: 'Something'

  infrastructure-services:
    nats:
    mongodb:
      external: True  # We have a MongoDB, but we run it on a different host. A service requiring MongoDB will not complain.

  deployment-target:
    hosts:
      localhost:
        ip: 127.0.0.1

Rolling out the project with Ansible
====================================

You can copy the created docker-compose file to the target (mostly together with the :file:`config_dir`) and run the update
using a remote connection like SSH.

But it is easier using some kind of Configuration management. Thus Ansible is coupled to the Framework. If you run
``fiot deploy my_deployment`` an Ansible playbook is generated and deployed to the configured target:

This will copy the :file:`docker-compose.yaml` and the :file:`config_dir` to the target, pull (and update) the Docker images
on the target and restart the services. If specified this works for many hosts in parallel.

Ansible needs to be installed manually on your machine for this to work.
