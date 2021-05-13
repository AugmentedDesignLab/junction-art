import unittest
from roadgen.HDMapBuilder import HDMapBuilder

class test_HDMapBuilder(unittest.TestCase):

    def setUp(self) -> None:
        self.hdMapBuilder = HDMapBuilder(20)
        pass

    
    def test_buildMap(self):
        self.hdMapBuilder.buildMap()
        pass