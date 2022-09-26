from typing import Dict, Type, Union, List

from pydantic import BaseModel

from fastiot import logging
from fastiot.core.data_models import FastIoTData


def parse_object(dic: Dict, data_model: Type[Union[Type[FastIoTData], BaseModel]]) -> \
        Union[Type[Union[FastIoTData, BaseModel]], None]:
    """
    This function will help you convert a dictionary to an instance, of which the class inherits
    FastIoTData or BaseModel.

    .. code:: python

        my_dict = {'name': 'test_dict', 'value': 123}

        obj = parse_object(my_dict, MyDataModel)
        >>> MyDataModel(name='test_dict', value=123)


    """
    if issubclass(data_model, FastIoTData) or issubclass(data_model, BaseModel):
        return data_model.parse_obj(dic)
    logging('parse_object').error('Please use the Data Model, which inherits FastIoTData or BaseModel')
    return None


def parse_object_list(dict_list: List[Dict], data_model: Type[Union[FastIoTData, BaseModel]]) -> \
        Union[List[Type[Union[FastIoTData, BaseModel]]], None]:
    """
    This function helps you to convert a list of dictionaries to a list of instance, of which the class
    inherits FastIoTData or BaseModel

    .. code:: python

        my_dict_list = [{'name': 'test_dict_1', 'value': 123}, {'name': 'test_dict_2', 'value': 23}]

        obj_list = parse_object_list(my_dict_list, MyDataModel)
        >>> [MyDataModel(name='test_dict_1', value=123), MyDataModel(name='test_dict_2', value=23)]

    """

    data_model_list = [parse_object(dict_data, data_model) for dict_data in dict_list]
    return data_model_list
