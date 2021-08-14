import numpy as np
import math

class Fov:
    @staticmethod
    def getFovFromMinCorner(minCorner):

        fov = (np.pi - minCorner) * 2
        if fov > np.pi:
            raise Exception(f"fov {math.degrees(fov)}")
        return fov
