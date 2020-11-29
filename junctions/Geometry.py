from abc import ABC, abstractmethod
import numpy as np
class Geometry(ABC):

    @staticmethod
    def headingsTooClose(h1, h2, threshold = 0.1):
        h1 = h1 % (np.pi*2)
        h2 = h2 % (np.pi*2)
        if abs(h1 - h2) <= threshold:
            return True
        return False