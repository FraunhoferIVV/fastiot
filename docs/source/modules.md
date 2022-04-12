# fastIoT modules

## Data dashboard


The module is used to show data from either a data bank or data gathered from live subscriptions in a simple web
application.


## OPC UA Reader

The machine monitoring acts as an opc ua client to read opc-ua data from an opc-ua server. It has various configuration
options. 

## Time series

The time series module subscribes to machine data and stores it as time series into mongodb. It can caches them and can
be flushed. There are also some configuration options, please refer to :ref:`time_series_env_variables`.
