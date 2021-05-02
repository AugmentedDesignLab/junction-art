from z3 import *
from roadgen.definitions.Point import Point


class IncidentPoint(Point):
    def __init__(self, id, originalPosition, nIncoming, nOutgoing, nHeading=None):
        super().__init__(id, originalPosition)
        self.nIncoming = nIncoming
        self.nOutgoing = nOutgoing
        self.nHeading = nHeading