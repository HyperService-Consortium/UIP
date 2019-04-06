
from enum import Enum


class StateType(Enum):
    unknown = 0
    init = 1
    inited = 2
    open = 3
    opened = 4
    closed = 5
