##################################
Running unit and integration tests
##################################

Testing within a microservice framework is a little more difficult compared to monolithic architectures as many tests
rely on the message broker to be available.

If created your deployment configurations and started the broker like describe in the last tutorial :ref:`label-cli-intro`
you should be able to simply start the tests with your IDE from the test-package automatically created.


As an alternative you can also use the command ``fiot run-tests``. This will even create a configuration if not yet done.
If you want this as a One-Shot-Solution you can also run the services specified in the integration test deployment,
execute the tests and stop everything afterwards: ``fiot run-tests --start-deployment``.

**Some remarks regarding configuration and environment variables:** The connection to the broker heavily depends on the
correct environment variables. This is not only needed for running locally, but also for the unittests.
The tests need to know at what host and port to look for the broker. Therefore when creating the docker-compose file that
will start the broker the ports are set. And those ports can be read into the tests so that a service started within a
test case can connect to the correct broker.

We will add more information about the test library later on. Stay tuned!