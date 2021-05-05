from z3 import IntVal
from enum import Enum, auto

class LogicalQuadrantType(Enum):
    TOP = auto()
    LEFT = auto()
    BOT = auto()
    RIGHT = auto()

    pass

class LogicalQuadrant:

    def __init__(self, nIncoming, nOutgoing, anglePresence=(False, True, False)):
        # self.nIncoming = IntVal(nIncoming) # conver to bit vectors
        # self.nOutgoing = IntVal(nOutgoing)
        self.nIncoming = nIncoming
        self.nOutgoing = nOutgoing
        self.anglePresence = anglePresence # clockwise. 

    
    def __str__(self):
        return f"(in: {self.nIncoming}, out: {self.nOutgoing})"