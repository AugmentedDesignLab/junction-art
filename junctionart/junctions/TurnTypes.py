from enum import Enum


class TurnTypes(Enum):

    LEFT = "LEFT"
    RIGHT = "RIGHT"
    STRAIGHT = "STRAIGHT"
    STRAIGHT_LEFT = "STRAIGHT_LEFT"
    STRAIGHT_RIGHT = "STRAIGHT_RIGHT"
    ALL = "ALL"
    UNDEFINED = "UNDEFINED"

    @staticmethod
    def getStraightOrLeft():
        return (TurnTypes.LEFT, TurnTypes.STRAIGHT_LEFT, TurnTypes.STRAIGHT)
    

    @staticmethod
    def getStraightOrRight():
        return (TurnTypes.STRAIGHT, TurnTypes.RIGHT, TurnTypes.STRAIGHT_RIGHT)

    @staticmethod
    def getAll(includeAll=True):
        if includeAll:
            return (TurnTypes.LEFT, TurnTypes.STRAIGHT_LEFT, TurnTypes.STRAIGHT, TurnTypes.RIGHT, TurnTypes.STRAIGHT_RIGHT, TurnTypes.ALL)
        else:
            return (TurnTypes.LEFT, TurnTypes.STRAIGHT_LEFT, TurnTypes.STRAIGHT, TurnTypes.RIGHT, TurnTypes.STRAIGHT_RIGHT)
