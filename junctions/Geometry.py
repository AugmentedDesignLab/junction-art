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

    

    @staticmethod
    def getLengthOfGeoms(geoms):
        """[summary]

        Args:
            geoms ([type]): List of Geometries of type Arc, Spiral, Line, ParamPoly3

        Returns:
            [type]: [description]
        """
        totalLength = 0
        for geom in geoms:
            _, _, _, length = geom.get_end_data(0, 0, 0)
            totalLength += length
        
        return totalLength