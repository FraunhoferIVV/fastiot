###################
Integrated Services
###################

FastIoT comes with some services prepacked.

*************
Core Services
*************

Core services are ready to use and just need some configuration. Please consult the documentation about what is needed.
Most of the time it boils down to either some environment variables and/ or a YAML-file.

.. seealso:: :ref:`configuration_for_service`

.. toctree::
   :maxdepth: 1
   :glob:

   api/fastiot_core_services/*

***************
Sample Services
***************

Sample services are ment to be a copy and paste solution for your own projects. Some like the
:mod:`fastiot_sample_services.producer` may help you when debugging your services immediately.

Others like :mod:`fastiot_sample_services.fastapi` provide some hints on how to integrate certain popular frameworks in
your own project. The documentation for the sample services may not be as extensive as the core services.

.. toctree::
   :maxdepth: 1
   :glob:

   api/fastiot_sample_services/*
