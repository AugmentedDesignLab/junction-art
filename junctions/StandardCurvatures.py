from enum import Enum
import numpy as np


class StandardCurvature(Enum):
    
    Sharp = 0.5
    MediumSharp = 0.1
    Medium = 0.05
    MediumWide = 0.02
    Wide = 0.01
    VeryWide = 0.005

    @staticmethod
    def values():
        return [e.value for e in StandardCurvature]

    
    @staticmethod
    def getRandomValue():
        values = StandardCurvature.values()
        return values[np.random.choice(len(values))]