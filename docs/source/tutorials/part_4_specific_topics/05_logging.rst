Customized logging
==================


In FastIoT Framework, there is a logging with default setting, it will configurate the format of logging messages.
With the :envvar:`FASTIOT_LOG_LEVEL` you can set the logging level. s. https://docs.python.org/3.10/howto/logging.html#logging-levels
It is possible to set the log level via integers, e.g. 10 for DEBUG; 20 for INFO etc., or via text, e.g. 'debug' or 'info' and so on.

Following code shows, how to import the customized logging:

.. code-block:: python

    from fastiot import logging

    logging.debug('This is debug message')
    logging.info('This is info message')

>>> YYYY-MM-DD HH:MM:SS.XXX: INFO     file.py/func:28: This is info message
