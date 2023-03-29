.. _tut-custom_infrastructure_services:
Adding custom infrastructure services to your project
=====================================================

As the FastIoT will take care of generating :file:`docker-compose.yaml` files for your project and for integration tests
it needs to know the services, e.g. databases, to load. Those services are named *Infrastructure Service* to
differentiate them between FastIoT Services.

Various services are already preconfigured and you only need to add those to your project. See
:mod:`fastiot.cli.common.infrastructure_services` for the services available.

To add your own service you have to follow a few basic steps:

1. Create the Service inheriting either from :class:`fastiot.cli.model.infrastructure_service.InfrastructureService` or if you only
   have some minor adjustments inherit from any service inheriting from
   :class:`fastiot.cli.model.infrastructure_service.InfrastructureService` itself.
   You may add those class anywhere in your project. It is recommended to use something like
   ``your_project_lib.extension.services``.
2. Add the corresponding import, e.g.  ``your_project_lib.extension.services`` to your :file:`configure.py` in your
   project root dir using the :attr:`fastiot.cli.model.project.ProjectContext.extensions`. Make sure this will really
   import the class.
3. You should now be able to add a service in your :file:`deployment.yaml` with the name you specified.
4. Build your configuration using :command:`fiot config`. If the command fails try to raise the debug level:
   :command:`FASTIOT_DEBUG_LEVEL="DEBUG" fiot config`
5. You should now have a docker-compose file with your new infrastructure service added!
