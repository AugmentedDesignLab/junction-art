from enum import IntEnum
import numpy as np


class StandardCurveTypes(IntEnum):
    Simple  = 1
    LongArc = 2
    S       = 3
    Poly    = 4
    Line    = 100 # must be the last element 


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
    def getRandomItem(includeLine = False):
        items = StandardCurveTypes.items()
        if includeLine:
            return items[np.random.choice(len(items))]
        else:
            return items[np.random.choice(len(items)-1)]