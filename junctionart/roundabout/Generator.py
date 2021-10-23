from abc import abstractmethod
from typing import List, Dict

class Generator:

    @abstractmethod
    def generateWithIncidentPointConfiguration(self, ipConfig: List[Dict]):
        pass
    