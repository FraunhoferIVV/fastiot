"""
Module for storing and retrieving Data
========================================

This Service is intended for saving data and the  requesting of historical data.

If you aren't using a docker-compose file generated with your project, you must also  set variables defined in ::class:: fastiot.env.env.InfluxDBEnv

By default, this module stores any message written under "Thing". The data is stored in InfluxDB and has the format:
    "measurement": name of the sensor
    "tags":
        "machine": name of the machine
    "fields":
        "value": you value," ",the unit of your value
    "time": the time the data was recorded

You can request the data with an  ::class:: fastiot.msg.hist.HistObjectReq . The default reply subject is "things" and
 returns the oldest 20 datasets of the last 30 days. When creating your own query, you need to specify a time range.

The response will be stored as an ::class:: fastiot.msg.hist.HistObjectResp
The Data stored in "values" has the format:
[data1, data2]
data:
..code:: python
{"machine": row.values.get("machine"),
                                "sensor": row.get_measurement(),
                                "value": row.get_value(),
                                "timestamp": row.get_time(),
                                }
If no data is found, the error code is 1.
"""