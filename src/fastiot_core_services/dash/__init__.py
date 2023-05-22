"""
=================
Dashboard Service
=================

This Module is able to show live data received from nats ('Things') collected by sensors in a web application.
Via callbacks a link from the web application back to the data bank shown is given.
Classes HistoricSensor and LiveSensor were added to modularise the code.
By setting HistoricSensor, this module will provide a link to download the historic data from the interval you selected.

To use this module some information is required:

Connection information to the database must be modified.

To show your data create a yaml file, like in the example below.
The start and end date of the first call of setup_historic_sensors Must be defined in the yaml file too.
When you change the date  for historic sensors in the Web interface the time will be set to 00:00 of the given date.
(You have to take this into account when requesting data)

If not data is shown make sure that all environmental variables are set correctly.
This concerns manly the connection data, like Ip address, port, the name of the Db or the collection name.


necessary yaml file

.. code-block:: yaml

    subject_name: 'thing.*' or 'thing.>' # this subject_name defines in which format the message is subscribed.
    #dashboards shown in the web applications.
    initial_start_date: now-30:00:00   #initial date shown in historic data. This can be set with either one of these
    initial_end_date: now              #formats:now, now-hh:mm:ss or Iso- Format: YYYY-MM-DDThh:mm:ss
    db:
    dashboards:                        #list of dashboards is used, to add another graph add to the list
      - name: Temperature of test      #name shown in the web application
        live_data: True                #False-> data is shown in the historic data format and taken out of data bank,
                                       #True -> data is shown in live data format and taken from nats-subscriptions
        refresh_time: 1000             #how fast data gets updated in ms, used only in live_data
        time_shown: 120                #for live data the maximum interval shown
        customer: a_customer           #customer to identify the sensor
        db: mongodb                    #write here what type of db your data is written in [mongoDB, influxDB] supported
        sensors:                       #list of sensors, to add another sensor to be shown in this graph add to the list
         - name: sensor_1              #name, module and machine used to identify the sensor. all are currently required
           machine: example_sam_m1     #the name is also used to name the trace in the graph
           module: a_module
         - name: sensor_2
           module: a_module
           machine: example_sam_m1
      - name: Influx_Test
        live_data: False
        refresh_time: 1000000
        time_shown: 120
        customer: a_customer
        db_type: influx
        sensors:
         - name: PM3-JWCO.opr:me
           machine: a_machine
           module: a_module
         - name: 36QM14.LF:av
           machine: a_machine
           module: a_module
         - name: 36QM14.CC:av
           machine: a_machine
           module: a_module
      - name: Pressure_Test
        live_data: False
        refresh_time: 1000000
        time_shown: 120
        customer: a_customer
        db_type: mongodb
        sensors:
         - name: temp_1
           machine: a_machine
           module: a_module
         - name: temp_2
           machine: a_machine
           module: a_module
         - name: temp_3
           machine: a_machine
           module: a_module



"""
