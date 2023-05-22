.. _configuration_for_service:

Configuration for a service
===========================

Using environment variables
---------------------------

A common way to pass configurations to software running in a container are environment variables. Those can easily be
configured in an file called :file:`.env`. See :ref:`deployment_yaml` for more information about passing environment
variables to the container.

We recommend to use environment variables for small configurations where only a few settings are needed and no complex
structures like large lists, etc. are necessary. Larger configurations should use yaml-files (s. next section).

Reading environment variables is fairly easy in Python, just use ``os.environ.get('YOUR_ENV_VAR')``. In this framework
a slightly more complex solution has been chosen for better documentation, usage within integration tests and
maintainability:

.. code-block:: python

  FASTIOT_MY_ENV_VAR = 'FASTIOT_MY_ENV_VAR'

  class MyEnv:
      @property
      def my_variable() -> int:
          """ .. envvar:: FASTIOT_MY_ENV_VAR

          use this to add some documentation on your variable!
          """
          return int(os.environ.get(FASTIOT_MY_ENV_VAR, 0)

  my_env = MyEnv()


  # Using is now quiet comfortable anywhere in your code:
  my_var = my_env.my_variable


Using YAML-Files
----------------

YAML, for yet another markup language, allows for more complex setups.
Reading a yaml-file is pretty easy, using :func:`fastiot.util.config_helper.read_config` to get the YAML-file as a
dictionary.
This works well for smaller configurations but you have to validate the configuration on your own (checking if mandatory
keys exist, …).

When working with more complex configurations it is recommended to add a configuration data model to your service.
This allows for easier validation (using Pydantic) and documentation of the expected options.
Also addressing parts of the documentation now does not rely on dictionary keys (usually as strings) any more but
on the Python class.
This will improve syntax completion in your IDE and thus make programming faster!

See the following example for more information about how to use custom configuration models.

.. code-block:: python

  from fastiot.core import FastIoTService
  from fastiot.util.config_helper import FastIoTConfigModel


  class MyExampleConfig(FastIoTConfigModel):
      """ This is an example configuration for a service with good ability for documentation. """

      config_name: str
      """ Set a name for the configuration or service"""
      config_value_x: int
      """ Provide a value for _x_ here """
      other_value_with_default: str = 'default'


  class MyService(FastIoTService):

    def __init__(self, **kwargs)
      super().__init__(**kwargs)
      my_config = MyExampleConfig.from_service(self)

      some_value = my_config.config_value_x


Please pay attention when instantiating multiple instances of a service. Each service needs to have the environment
variable :envvar:`FASTIOT_SERVICE_ID` set, resulting in reading out different configuration files for each service.
