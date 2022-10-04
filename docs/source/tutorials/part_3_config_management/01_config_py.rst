.. _tut-configure_py:

########################################
Project configuration using configure.py
########################################

The basic configuration for your project is read from the file :file:`configure.py` in your project root dir.

The file follows the data model specified in :class:`fastiot.cli.model.project.ProjectConfig`.

Some attributes you may add in many cases are the specification of a module with with your unittests
(:attr:`fastiot.cli.model.project.ProjectConfig.test_package`) and a deployment to run for the integration tests
(:attr:`fastiot.cli.model.project.ProjectConfig.integration_test_deployment`).

FastIoT usually detects services and deployments by itself. If you need to manage those lists yourself (attributes
:attr:`fastiot.cli.model.project.ProjectConfig.services`) or :attr:`fastiot.cli.model.project.ProjectConfig.deployments`)
you can use the methods :meth:`fastiot.cli.helper_fn.find_services` and :meth:`fastiot.cli.helper_fn.find_deployments`
to create the corresponding lists.

Minimal setup
-------------

As FastIoT tries to set sensible defaults the :file:`configure.py` can stay pretty small:

.. code-block:: python

  project_namespace = 'your_project'

