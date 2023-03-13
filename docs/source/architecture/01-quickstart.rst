.. _quickstart:
***********
Quick start
***********

*This should help getting started quickly. A more detailed description can be found in the tutorials.*

It is always recommended to use a separate virtual environment for each project, so let’s create one: ``python3 -m venv venv`` and use it: ``source venv/bin/activate``

Afterwards you can install FastIoT: ``python3 -m pip install fastiot``

To setup a new project with the name ``my_first_project`` you can now run: ``fiot create new-project my_first_project``

Within this repository you can find some sample services to use as template.
Or you can simply ask the CLI to create a new services: ``fiot create new-service my_first_service``.
You should now find a service stub in your project to be extended with your application logic.
The service will be added to the deployment "full" automatically.

You can now also create deployment configurations (e.g. a ``docker-compose.yaml``) using ``fiot config`` and build 
containers for your project using ``fiot build``.

As the service has been added to a deployment automatically you now start the service (with broker) with the command
``fiot start full``. You should see the log messages from sending and receiving data. To cancel just press
:kbd:`Ctrl` + :kbd:`C`.

For a more comprehensive list of features, a guide to the project structure please refer to the complete documentation.

To run services locally, in your IDE or within a container please refer to the tutorials section in this documentation.
