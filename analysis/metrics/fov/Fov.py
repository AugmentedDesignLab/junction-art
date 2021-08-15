import numpy as np
import math

class Fov:
    @staticmethod
    def getFovFromMinCorner(minCorner):

        fov = (np.pi - minCorner) * 2
        if fov > np.pi * 1.1:
            raise Exception(f"fov {math.degrees(fov)}")
        return fov
