Writing unit and integration tests
==================================


Testing the interaction of your services with the broker and other services is important.

FastIoT provides some methods to interact with your services more easy.

Basic walk through with examples
--------------------------------

Most of the steps including generating the configuration have probably already been done by now, but let’s do it
complete.

1. Add the services you need for testing, e.g. `nats` or `mongodb` to the :file:`deployments.yaml` inside your
   integration test environment.
   `nats` should already be in there, if you used the CLI to create your project.
2. Run :command:`fiot config` to create the configuration in :file:`build/deployments`
3. Start your integration test deployment: :command:`fiot start --use-test-deployment`
4. Create a Unit Test in :file:`your_project_tests`, s. example code below.

.. code:: python

  import unittest

  from fastiot.core.broker_connection import NatsBrokerConnection
  from fastiot.core.time import get_time_now
  from fastiot.msg.thing import Thing
  from fastiot.testlib import populate_test_env

  class TestMyService(unittest.IsolatedAsyncioTestCase):
  """ Asynchronous test case """

    async def asyncSetUp(self):
          """ We have to usual setup, but here as `asyncSetUp`.
          populate_test_env()  # We add the environment variables we generated in :file:`build/deployment`
          self.broker_connection = await NatsBrokerConnection.connect()  # Initiate a broker connection

      async def test_something(self):  # We have an asynchronous test case
          async with MyService(broker_connection=self.broker_connection) as service:
          # Services can be started using `async with`
              await self.broker_connection.publish(Thing.get_subject(name='unfiltered'),
                                                   Thing(machine='SomeMachine', name="LoggedSensor", value=24,
                                                         timestamp=get_time_now(), measurement_id="1"))
              # We just published a message

              # Now we can test something inside your service, e.g. if the message has been received.
              # self.assertEqual(24, service.last_value)

See :class:`fastiot_tests.core_services.test_nats_logger.TestNatsLogger` for a small but fully working example.


An alternative way is to start the service as a thread.
Add imports and actual logic as needed.

.. code:: python

  class TestMyService(unittest.IsolatedAsyncioTestCase):

      async def asyncSetUp(self):
          populate_test_env()
          self.broker_connection = await NatsBrokerConnection.connect()
          await self._start_service()

      async def _start_service(self):
          service = MyService(broker_connection=self.broker_connection)
          self.service_task = asyncio.create_task(service.run())
          await asyncio.sleep(0.05)  # Wait a little for the service to be ready!

      async def asyncTearDown(self):
          self.service_task.cancel()
          await self.broker_connection.close()

      async def test_something(self):
          self.broker_connection.publish(…)




Setting environment variables
-----------------------------

Sometimes you may want to have an environment variable to be read in your service.
The simples way is to just add ``os.environ['MY_VAR'] = 'something'`` to your test code.

Be aware, that those variables may stay alive for further tests and thus could interact.

A more secure way is to use `mocking <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch.dict>`_
Use the dictionary ``os.environ`` to patch.

See :class:`fastiot_tests.cli.test_config_cmd.TestConfigCommand` for an example.


Opening ports in your services
------------------------------

If your service opens ports it is recommended to set some random port for the test.
This way the chances for conflicts on the CI runner are reduced.
FastIoT provides a simple option to look for an open port using :meth:`fastiot.util.ports.get_local_random_port`.

.. code:: python

  from fastiot.util.ports import get_local_random_port


  class MyTestCase(unittest.IsolatedAsyncioTestCase):

      async def asyncSetUp(self):
          populate_test_env()
          os.environ[MY_PROJECT_A_SERVICE_PORT] = str(get_local_random_port())
          # We have defined a variable in the manifest, this name has to be used here
