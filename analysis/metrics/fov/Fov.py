import numpy as np
import math
import logging

class Fov:
    @staticmethod
    def getFovFromMinCorner(minCorner):

        fov = (np.pi - minCorner) * 2
        if fov > np.pi * 1.5:
            logging.warning(f"fov {math.degrees(fov)}")
            # raise Exception(f"fov {math.degrees(fov)}")
        return fov
