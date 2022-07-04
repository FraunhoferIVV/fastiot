================
fastIoT Taxonomy
================

As a project will contain many different aspects this is a clear definition of all aspects:

Package
-------
In Python and fastIoT a package is a directory containing at least a :file:`__init__.py` and various other Python-files
mostly referred to as Python-Module.

Service
-------
A microservice written for and with the fastIoT Framework. In the former framework `SAM` this used to be called
`Module`.

Third Party Service
-------------------
Services written by others to load into the project. Mostly this concerns message broker, database, …

Deployment
----------
A set of deployment configuration and various service settings to be rolled out e.g. to a customer. Usually also a
deployment to be running when doing integration tests within a CI-runner is defined in a project. This is from a strict
view not a deployment but still fits in best within this category.