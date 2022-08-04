*********************
Architecture Overview
*********************

FastIoT is designed as a service architecture.

We use the following technologies to support the architecture:
 * `nats.io <https://nats.io/>`_ as a message broker for inter module communication.
 * `Docker <https://docker.com/>`_ for module runtime management with `docker-compose <https://docs.docker.com/compose/reference/>`_  for managing many containers
    * In production there is one separate docker container for each FastIoT Service
    * For testing purposes modules can be simulated or run locally and interact with other FastIoT or infrastructure services running in docker containers
 * MongoDB, MariaDB and others for data storage, s. :mod:`fastiot.db` for information on database handling.


Modules and Messaging Basics
============================

Messages:
 * ... can be sent or received by modules via the NATS Broker using publish and subscribe.
 * ... are sent via a NATS Broker subject. The subject has a name, a message type and optionally a response type.

Services:
 * ... are configured via environment variables or yaml-Files, depending on your needs
 * ... are executed in a Docker environment (for production), via command line, or within an IDE like PyCharm (for development)
 * ... connect themselves to the NATS Broker
 * ... publish and subscribe to the subjects of the NATS Broker
 * ... log their messages to the NATS Broker
