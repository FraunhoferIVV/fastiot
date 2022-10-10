#######################################
Customized logging
#######################################


In FastIoT Framework, there is a logging with default setting, it will configurate the format of logging messages.
With the :envvar:`FASTIOT_LOG_LEVEL_NO` you can set the logging level. s. https://docs.python.org/3.10/howto/logging.html#logging-levels

Following code shows, how to import the customized logging:

.. code-block:: python

    from fastiot import logging

    logging.debug('This is debug message')
    logging.info('This is info message')

>>> YYYY-MM-DD HH:MM:SS.XXX: INFO     file.py/func:28: This is info message
