*********************
Architecture Overview
*********************

fastIoT is designed as a service architecture.

We use the following technologies to support the architecture:
 * NATS as a message broker for inter module communication.
 * Docker for module runtime management
    * In production there is one separate docker container for each SAM module
    * For testing purposes modules can be simulated or run locally and interact with other modules or services running in docker containers
 * MongoDB and MariaDB for data storage


Modules and Messaging Basics
============================

Messages:
 * ... can be sent or received by modules via the NATS Broker using publish and subscribe.
 * ... are sent via a NATS Broker subject. The subject has a name, a message type and optionally a response type.

Services:
 * ... are configured via environment variables.
 * ... are executed in a Docker environment (for production), via command line, or within an IDE like PyCharm (for development)
 * ... connect themselves to the NATS Broker
 * ... publish and subscribe to the subjects of the NATS Broker
 * ... log their messages to the NATS Broker

