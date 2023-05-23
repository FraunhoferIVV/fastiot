"""
FastIoT Service to save "Object" into mongodb,
see :func:`fastiot.db.mongodb_helper_fn.get_mongodb_client_from_env`

========================================

This Service is intended for saving "Object" inheriting the :class:`fastiot.core.data_models.FastIoTData`,
and requesting of historical object data. This Service is also designed to save one data type, for demanding saving
multiple data types, you can instance multiple Services, using config file.

Your Object will be saved in Dictionary in such format, 'yyy' stands for the unpacked Attributes of Object:

.. code:: python

  {'_id': 'xxx', '_subject': 'xxx', '_timestamp': 'xxx', 'yyy': 'xxx', 'yyy': 'xxx}


In Order to use this Service, you must set a config file named :file:`ObjectStorageService.yaml` or
:file:`ObjectStorageService_1.yaml` in :file:`my_deployment/config_dir`, for reading :file:`ObjectStorageService_1.yaml`
:envvar:`FASTIOT_SERVICE_ID` must be set.

The configuration is based on the configuration model
:class:`fastiot_core_services.object_storage.config_model.ObjectStorageConfig`.
Please refer to the model for a description of the single fields.

The following example should provide you with a working configuration:

.. code:: yaml

  search_index:
    thing:
      - "_subject" , "_timestamp"
      - "_id"
  subscriptions:
    'thing.*':
      collection: 'thing'
      reply_subject_name: 'objects'
      enable_overwriting: false
      identify_object_with:
        - "measurement_id"
        - "_timestamp"


Remarks:
* ``search_index`` defines the MongoDB index to speed up the query.
  ``_subject`` and ``_timestamp`` are defined as compound index in the above example.
* ``subject_name`` is the subject, where you send your data.
* ``enable_overwriting`` is a boolean flag for object overwriting
* ``identify_object_with`` defines object fields, which define the whole object with its uniqueness
  The other fields will be overwritten respectively.
  Needed only if ``enable_overwriting`` set on ``true``

.. versionchanged:: 0.2.101
   Using ``subject_name`` to define the subject this service will respond is deprecated. Use the new field
   ``reply_subject_name`` instead. The old style will continue to work but throw a warning till it will be removed
   completely.

.. versionadded:: 0.8.10

   * Added mode for overwriting objects.
   * Added option for compound indices

.. versionchanged:: 0.9.33
   Migrating to model based configuration with
   :class:`fastiot_core_services.object_storage.config_model.ObjectStorageConfig`


You can assign the subject like following ``MyDataType`` or ``my_data_type``,
both will return you a right subject name format: ``v1.my_data_type``.

**CAUTION!**: Thing will be instanced with different names. So by subscribing ``thing`` please always with a ``*``.
For understanding, you may reference to https://docs.nats.io/nats-concepts/subjects.


The other functionality for Object Storage Service is, you can make a request of the historical data stored in the
MongoDB.
To request the historical data, you need to instantiate :class:`fastiot.msg.hist.HistObjectReq`,
with subject_name 'reply_object'.
The code will look like:

.. code:: python

  hist_req_msg = HistObjectReq(dt_start=datetime(), dt_end=datetime(), limit=10, subject_name='logged_subject')
  subject = hist_req_msg.get_reply_subject(name='my_set_reply_subject_name')

**CAUTION!** This subject_name should be the same as, which you have defined in ObjectStorageService.yaml.
This request will reply to you a list of dictionaries.
Then you can convert it to your own data type using :func:`fastiot.util.object_helper.parse_object_list`.
"""
