"""Teach this SDK build about Bradbury's status code 14 (ACTIVATED)."""
from genlayer_py.types import transactions as _t

class _Activated:
    value = "ACTIVATED"

def apply():
    mapping = _t.TRANSACTION_STATUS_NUMBER_TO_NAME
    if "14" not in mapping: mapping["14"] = _Activated()
    if 14 not in mapping: mapping[14] = _Activated()
