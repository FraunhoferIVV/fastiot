"""
Service to read out OPC UA data
===============================

For configuration please consult :class:`fastiot_core_services.machine_monitoring.env.OPCUAEnv` and use a CSV-file.

_Documentation to be continued_

"""
import logging

logging.getLogger('opcua').setLevel(level=logging.ERROR)
