from enum import Enum
import numpy as np


class StandardCurvature(Enum):
    
    UltraSharp = 0.2
    Sharp = 0.15
    MediumSharp = 0.1
    Medium = 0.08
    MediumWide = 0.06
    Wide = 0.04
    VeryWide = 0.03
    UltraWide = 0.01

    @staticmethod
    def values():
        return [e.value for e in StandardCurvature]

    
    @staticmethod
    def getRandomValue():
        values = StandardCurvature.values()
        return values[np.random.choice(len(values))]