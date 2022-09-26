"""
FastIoT Service to save "Object" into mongodb,
see :func:`fastiot.db.mongodb_helper_fn.get_mongodb_client_from_env`

========================================

This Service is intended for saving "Object" inheriting the :class:`fastiot.core.data_models.FastIoTData`,
and requesting of historical object data.

Your Object will be saved in Dictionary in such format:

.. code:: python

  {'_id': 'xxx', '_subject': 'xxx', '_timestamp': 'xxx', 'Object': 'xxx'}


In Order to use this Service, you must set a config file named ObjectStorageService.yaml in my_deployment/config_dir.

.. code:: yaml

  search_index:
   - "_subject"
   - "_timestamp"
  collection: 'object_storage'
  subject: 'thing.*'

  
or the subject can be your own Data Model, which inherits :class:`fastiot.core.data_models.FastIoTData`, e.g.:

.. code:: python

  class MyDataType(FastIoTData)

You can assign the subject like following 'MyDataType' or 'my_data_type',
both will return you a right subject name format: 'v1.my_data_type'.
**CAUTION**: Thing will be instanced with different names. So by subscribing **thing** please always with a *****.
For understanding you can reference this https://docs.nats.io/nats-concepts/subjects.


For quick query data in mongodb, search_index must be set.
Through collection, the collection will be defined, where you save your data.
Furthermore, the subject must be set, it indicates, which topic the nats client function subscripts.

The other functionality for Object Storage Service is, you can make a request of the historical data,
which are saved in Mongodb.
To request the historical data, you need to instantiate :class:`fastiot.msg.hist.HistObjectReq`,
with subject_name 'reply_object'.
The code will look like:

.. code:: python

  hist_req_msg = HistObjectReq(dt_start=datetime(), dt_end=datetime(), limit=10, subject_name='test_subject')
  subject = ReplySubject(name='reply_object', msg_cls=HistObjectReq, reply_cls=HistObjectResp)


This request will reply to you a List of Dictionary.
Then you can convert it to your own data type using :func:`fastiot.helpers.object_helper.parse_object_list`.
"""
