from enum import Enum
import numpy as np


class StandardCurvature(Enum):
    
    UltraSharp = 0.8
    Sharp = 0.6
    MediumSharp = 0.4
    Medium = 0.2
    MediumWide = 0.1
    Wide = 0.06
    VeryWide = 0.03
    UltraWide = 0.01

    @staticmethod
    def values():
        return [e.value for e in StandardCurvature]

    
    @staticmethod
    def getRandomValue():
        values = StandardCurvature.values()
        return values[np.random.choice(len(values))]