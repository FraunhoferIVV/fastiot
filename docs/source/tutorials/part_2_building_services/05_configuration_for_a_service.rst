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
Reading a yaml-file is pretty easy, using :func:`fastiot.util.read_yaml.read_config`.

Please pay attention when instantiating multiple instances of a service. Each service needs to have the environment
variable :envvar:`FASTIOT_SERVICE_ID` set, resulting in reading out different configuration files for each service.
