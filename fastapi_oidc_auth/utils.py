import functools
from typing import Dict


def dict_rgetattr(obj: Dict, attr: str):
    def _getattr(obj: Dict, attr: str):
        return obj[attr]

    return functools.reduce(_getattr, [obj] + attr.split("."))
