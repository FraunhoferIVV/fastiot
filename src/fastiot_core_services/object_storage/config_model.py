from typing import Dict, List, Union

from pydantic import BaseModel

from fastiot.util.config_helper import FastIoTConfigModel


class SubscriptionConfig(BaseModel):
    """ Configuration for each subscription"""
    collection: str
    """ MongoDB collection to store the data in """
    reply_subject_name: str = ""
    """ The subject this services listens for Historic Object Requests (:class:`fastiot.msg.hist.HistObjectReq`) """
    enable_overwriting: bool = False
    """ Overwrite data in the MongoDB if it matches with 
    :attr:`fastiot_core_services.object_storage.config_model.SubscriptionConfig.identify_object_with`"""
    identify_object_with: List[str] = []
    """
    Set the fields identifying an object to overwrite. All values coming with the same fields set will be overwritten.     
    """


class ObjectStorageConfig(FastIoTConfigModel):
    """ Base configuration for an object storage service """
    search_index: Dict[str, List[Union[str, List[str]]]] = {}
    """
    Define search indices to be added to the database here to speed up the query.
    Use a dictionary with the collection as key.
    You may provide a single entry (string type) to create a single index. 
    To create a multi-index simply provide a list of strings with the corresponding fields in the MongoDB here. 
    """
    subscriptions: Dict[str, SubscriptionConfig] = {}
    """
    Add subscriptions here, the key is the subscription like ``thing.*``. 
    """
