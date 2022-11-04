from typing import Dict, List


def kebab_case_to_snake_case(d: Dict):
    """
    Converts keys of dictionary recursivly from kebab case, e.g. 'my-key' to snake case, e.g. 'my_key'.
    """

    keys = list(d.keys())
    for key in keys:

        if isinstance(d[key], dict):
            kebab_case_to_snake_case(d=d[key])
        elif isinstance(d[key], list):
            _kebab_case_to_snake_case_for_list(d[key])

        new_key = key.replace('-', '_')
        if key != new_key:
            d[new_key] = d[key]
            del d[key]


def _kebab_case_to_snake_case_for_list(l: List):
    for item in l:
        if isinstance(item, dict):
            kebab_case_to_snake_case(item)
        elif isinstance(item, list):
            _kebab_case_to_snake_case_for_list(item)
