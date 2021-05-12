from z3 import IntVal

from enum import Enum, auto


class DirectionQuadrantType(Enum):

    TOP = auto()

    LEFT = auto()

    BOT = auto()

    RIGHT = auto()
    pass

class DirectionQuadrant:


    def __init__(self, nIncoming, nOutgoing, anglePresence=(False, True, False)):
        """[summary]

        Args:
            nIncoming ([type]): [description]
            nOutgoing ([type]): [description]
            anglePresence (tuple, optional): Not implemented. Want to divide the quadrant into 3 parts. directions parallel, directions going left, directions going right.. Defaults to (False, True, False).
        """

        # self.nIncoming = IntVal(nIncoming) # conver to bit vectors

        # self.nOutgoing = IntVal(nOutgoing)
        self.nIncoming = nIncoming
        self.nOutgoing = nOutgoing
        self.anglePresence = anglePresence # clockwise. 

    

    def __str__(self):

        return f"(in: {self.nIncoming}, out: {self.nOutgoing})"