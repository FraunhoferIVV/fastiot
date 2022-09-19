"""
FastIoT Service to save "Object" into mongodb,
see :func:`fastiot.db.mongodb_helper_fn.get_mongodb_client_from_env`

========================================

This Service is intended for saving "Object" inheriting the :class:`fastiot.core.data_models.FastIoTData`,
and requesting of historical object data.

Your Object will be saved in Dictionary in such format:

>>> {'_id': 'xxx', '_subject': 'xxx', '_timestamp': 'xxx', 'Object': 'xxx'}

In Order to use this Service, you must set a config file named ObjectStorageService.yaml in my_deployment/config_dir.

>>> search_index:
>>>  - "_subject"
>>>  - "_timestamp"
>>> collection: 'object_storage'
>>> subject: 'thing.*'

or the subject can be your own Data Model, which inherits :class:`fastiot.core.data_models.FastIoTData`, e.g. 'my_data_model'.

For quick query data in mongodb, search_index must be set.
Through collection, the collection will be defined, where you save your data.
Furthermore, the subject should also be set, it indicates, which topic the nats client function subscripts.

The other functionality for Object Storage Service is, you can make a request of the historical data,
which are saved in Mongodb.
To request the historical data, you need to instantiate :class:`fastiot.msg.hist.HistObjectReq`.
This request will reply to you a List of Dictionary. Then you can convert it to your own data type.
"""
