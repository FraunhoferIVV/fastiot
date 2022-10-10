from enum import Enum


class OPCUARetrievalMode(str, Enum):
    subscription = 'subscription'
    polling = 'polling'
