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

##########
Quickstart
##########

.. toctree::
   :maxdepth: 2

   quickstart



######################
Framework architecture
######################

.. toctree::
   :maxdepth: 2

   architecture_index


#########
Tutorials
#########

The tutorials will guide you step by step through certain topic to get started developing microservices with FastIoT.

.. toctree::
   :maxdepth: 2
   :glob:

   tutorials/*
 
###################
Integrated Services
###################

FastIoT comes with some services prepacked.

Core services are ready to use and just need some configuration. Please consult the documentation about what is needed.
Most of the time it boils down to either some environment variables and/ or a YAML-file.

Sample services are ment to be a copy and paste solution for your own projects. Some like the
:mod:`fastiot_sample_services.producer` may help you when debugging your services immediately.

Others like :mod:`fastiot_sample_services.fastapi` provide some hints on how to integrate certain popular frameworks in
your own project. The documentation for the sample services may not be as extensive as the core services.

.. toctree::
    :maxdepth: 2
    :glob:

    services


#############
API Reference
#############

.. toctree::
    :maxdepth: 2
    :glob:

    fastiot_api

******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
