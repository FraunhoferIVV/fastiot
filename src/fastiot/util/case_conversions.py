from typing import Dict


def kebab_case_to_snake_case(d: Dict):
    """
    Converts keys of dictionary recursivly from kebab case, e.g. 'my-key' to snake case, e.g. 'my_key'.
    """
    keys = list(d.keys())
    for key in keys:

        if isinstance(d[key], dict):
            kebab_case_to_snake_case(d=d[key])

        new_key = key.replace('-', '_')
        if key != new_key:
            d[new_key] = d[key]
            del d[key]
