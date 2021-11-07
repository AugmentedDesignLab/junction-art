from abc import abstractmethod
from typing import List, Dict

class Generator:

    @abstractmethod
    def generateWithIncidentPointConfiguration(self, ipConfig: List[Dict], firstRoadId=0, maxLanePerSide=2, minLanePerSide=0, skipEndpoint=None, odrId=0):
        pass
    