=================
FastIoT Framework
=================

Welcome to FastIoT’s documentation.

FastIoT is a framework for rapid development of IIoT-Systems using Python as main programming language. It helps to set
up a micro-service architecture and create services. The development has been started as basis for various research
projects at Fraunhofer IVV, Dresden, Germany.

To get started quickly it is equipped with a powerful command line interface (CLI): fiot. This helps setting up a new
project, create new services and run tests. It also supports creating cross-architecture Docker-containers and
deployment configurations with docker-compose files and Ansible playbooks to bring the software to the systems they
belong. Run ``fiot --help`` for a full list of features.

As for now the overall framework has only been used and tested on Linux systems.

If you use this framework in your scientific projects please cite:
  Tilman Klaeger, Konstantin Merker, "FastIoT – A Holistic Approach for Rapid Development of IIoT Systems", 2022.
  https://doi.org/10.48550/arXiv.2201.13243.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


*************************************
Framework architecture and quickstart
*************************************

.. toctree::
   :maxdepth: 1
   :glob:

   architecture/*


*********
Tutorials
*********

.. toctree::
   :maxdepth: 2
   :glob:

   tutorials/*
 
********
Services
********

Please have a look at the API documentation for core services to provide basic functionality and for example services.
Those will provide you with basic ideas how to do integration tasks and develop you own services.

- :mod:`fastiot_core_services`
- :mod:`fastiot_sample_services`


*************
API Reference
*************

.. toctree::
    :maxdepth: 1

    fastiot

******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
