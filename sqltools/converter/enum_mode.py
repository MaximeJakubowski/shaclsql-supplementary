from enum import Enum


class Mode(Enum):
    NQ_TO_TTL = 1
    NQ_TO_CSV = 2
    NQ_TO_DB = 3
    TTL_TO_CSV = 4
    TTL_TO_DB = 5
    CSV_TO_DB = 6
