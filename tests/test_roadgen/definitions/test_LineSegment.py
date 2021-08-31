import unittest

from junctionart.roadgen.definitions.LineSegment import LineSegment

class test_LineSegment(unittest.TestCase):

    def test_CheckConstraint(self):

        ls = LineSegment(id = 'l1', distance = 100)
        print(ls.constraint())

        ls2 = LineSegment.createFromPoints('l2', (0, 0), (3, 4))
        print(ls2.constraint())
