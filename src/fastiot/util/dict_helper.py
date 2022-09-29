from typing import Dict

from fastiot import logging


def dict_subtract(dict_1: Dict, dict_2: Dict) -> Dict:
    """
    With this function, you can subtract two dictionaries,
    if there are common keys in these dictionaries.
    *dict_1* and *dict_2* can be minuend and subtrahend, so the order does not matter.

    .. code:: python

        dict_1 = {'a': '123', 'b': '1234', 'c': 12345}
        dict_2 = {'a': '1', 'b': 123, 'c': 15, 'd': 'test'}

        dict_expected = dict_subtract(dict_1, dict_2)
        >>> {'d': 'test'}


    """
    if len(set(dict_1.keys()) & set(dict_2.keys())):
        if len(dict_1.keys()) > len(dict_2.keys()):
            all(map(dict_1.pop, dict_2))
            return dict_1
        else:
            all(map(dict_2.pop, dict_1))
            return dict_2
    else:
        logging('dict_subtract').error('No common keys in the dictionaries')
        return None
