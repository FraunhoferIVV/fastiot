FastIoT Taxonomy
================

As a project will contain many different aspects this is a clear definition of all aspects:

:Package: In Python and FastIoT a package is a directory containing at least a :file:`__init__.py` and various other Python-files
  mostly referred to as Python-Module.

:FastIoT Service: A microservice written for and with the FastIoT Framework. Often this may only be called `Service` as shorthand.
  In the former framework `SAM` this used to be called `Module`.

:Infrastructure Service: Services written by others to load into the project. Mostly this concerns message broker, database, …

:Deployment: A set of deployment configuration and various service settings to be rolled out e.g. to a customer as a set
  of containers managed within a :file:`docker-compose.yaml`. Usually also a deployment to be running when doing
  integration tests within a CI-runner is defined in a project. This is from a strict view not a deployment but still
  fits in best within this category.

