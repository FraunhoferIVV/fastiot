from enum import Enum


class OPCUARetrievalMode(str, Enum):
    subscription = 'subscription'
    polling = 'polling'
    polling_always = 'polling_always'
