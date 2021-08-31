import unittest
from junctionart.library.Combinator import Combinator

class test_Combinator(unittest.TestCase):

    def test_nP2(self):

        items = [1, 2, 4]
        permutations = Combinator.nP2(items)
        print(permutations)
        assert len(permutations) == 6

        items = [1, 2]
        permutations = Combinator.nP2(items)
        print(permutations)
        assert len(permutations) == 2
        