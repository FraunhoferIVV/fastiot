"""
Module for storing and retrieving time series data
==================================================

This Service is intended for saving data and the  requesting of historical data.

If you aren't using a docker-compose file generated with your project, you must also  set variables defined in
:class:`fastiot.env.env.InfluxDBEnv` to connect to the InfluxDB.
Some adjustments to this service can be done using :class:`fastiot_core_services.time_series.env.TimeSeriesConstants`.

By default, this module stores any message written under "Thing". The data is stored in InfluxDB and has the format:

..
    "measurement": name of the sensor
    "tags":
        "machine": name of the machine
    "fields":
        "value": you value," ",the unit of your value
    "time": the time the data was recorded

You can request the data with an :class:`fastiot.msg.hist.HistObjectReq` with topic ``things``. By default, it returns
the oldest 20 datasets of the last 30 days. When creating your own query, you must specify a time range.

The response will be returned as an :class:`fastiot.msg.hist.HistObjectResp`
The Data stored in "values" has the format: ``[thing1, thing2]`` where thing is formatted as a dictionary.

A short example:

.. code:: python

  from fastiot.util.object_helper import parse_object_list
  from fastiot.msg import Thing, HistObjectReq, HistObjectResp

  my_query = HistObjectReq()  # Create a request/ query
  result_dict: HistObjectResp = await self.broker_connection.request(my_query)  # Send request to broker
  result = parse_object_list(result_dict.values, Thing)  # Parse returned dictionary to List[Thing]

If no data is found, the error code (:attr:`fastiot.msg.hist.HistObjectResp.error_code`) is 1.
"""
