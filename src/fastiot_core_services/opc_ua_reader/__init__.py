"""
Service to read out OPC UA data
===============================

For configuration please consult :class:`fastiot_core_services.opc_ua_reader.env.OPCUAEnv` and use a CSV-file.

The main idea is to configure the opc-ua nodes via a csv-file and deploy this service to publish the data as
FastIoT-Things on a nats broker. See below example how to create your CSV-file.

Features included:
 * Running multiple instances with different configurations
 * Different modes (polling & subscriptions)
 * A variety of connection params, e.g. security strings
 * Error handling of opcua connections

Known limitations:
 * No "auto"-detection of opc-ua nodes supported
 * OPC-UA nodes must always be specified with nodeid (no browse name support)
 * No dynamic parsing of opc-ua nodes
 * No support of opc-ua functions
 * No support of opc-ua historic requests
 * Only nats-broker as data output supported


Example CSV configuration
-------------------------

Example CSV, to be stored as :file:`opc_ua_reader_things.csv` in a directory defined with
:envvar:`FASTIOT_OPC_UA_CONFIG_NAME` in the :file:`config_dir`.

.. code-block::

   nodeid,thing_name,machine
   ns=2;i=5,a_sensor,sim_machine

"""
import logging

logging.getLogger('opcua').setLevel(level=logging.ERROR)
