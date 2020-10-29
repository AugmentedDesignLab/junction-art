import unittest

import numpy as np
import os, dill
import pyodrx 
from junctions.JunctionMerger import JunctionMerger
import extensions

class test_JunctionMerger(unittest.TestCase):

    def setUp(self):
        with(open('F:\\myProjects\\av\\junction-art\\output\\_harvestedOrds.dill', 'rb')) as f:
            self.odrDic = dill.load(f)

        outputDir = os.path.join(os.getcwd(), 'output')
        self.merger = JunctionMerger(outputDir=outputDir)

    
    def test_merge2R2L(self):
            odrs = self.odrDic['0.3141592653589793']
            odrs2 = [odrs[0], odrs[5]]
            newOdr = self.merger.merge2R2L(odrs2)
            extensions.view_road(newOdr,os.path.join('..','F:\\myProjects\\av\\esmini'))