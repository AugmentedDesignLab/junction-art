from enum import IntEnum
import numpy as np


class StandardCurveTypes(IntEnum):
    Simple  = 1,
    LongArc = 2,
    S       = 3,
    Line    = 4


    @staticmethod
    def values():
        return [e.value for e in StandardCurveTypes]

    
    @staticmethod
    def getRandomValue():
        values = StandardCurveTypes.values()
        return values[np.random.choice(len(values))]

    

    @staticmethod
    def items():
        return [e for e in StandardCurveTypes]

    
    @staticmethod
    def getRandomItem():
        items = StandardCurveTypes.items()
        return items[np.random.choice(len(items))]