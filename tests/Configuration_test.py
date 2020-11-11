import unittest
from ..library.Configuration import Configuration

class ConfigurationTest(unittest.TestCase):


    def test_Get(self):
        configuration = Configuration()
        testVal = configuration.get('test2.test22')
        assert testVal == 'this is something'
