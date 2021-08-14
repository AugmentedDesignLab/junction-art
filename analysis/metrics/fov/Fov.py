import numpy as np

class Fov:
    @staticmethod
    def getFovFromMinCorner(minCorner):

        return (np.pi - minCorner) * 2
