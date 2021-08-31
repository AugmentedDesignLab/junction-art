import unittest

import numpy as np
import os, dill
import pyodrx 
from junctions.JunctionMerger import JunctionMerger
import junctionart.extensions as extensions
from library.Configuration import Configuration

class test_JunctionMerger(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        with(open('F:\\myProjects\\av\\junction-art\\output\\harvested2R2LOrds.dill', 'rb')) as f:
            self.odrDic = dill.load(f)

        outputDir = os.path.join(os.getcwd(), 'output')
        self.merger = JunctionMerger(outputDir=outputDir, outputPrefix="test_")

    
    def test_merge2R2L(self):
        odrs = self.odrDic['0.3141592653589793']
        odrs2 = [odrs[0], odrs[2]]
        newOdr = self.merger.merge2R2L(odrs2)
        extensions.view_road(newOdr,os.path.join('..',self.configuration.get("esminipath")))
        # odrs = self.odrDic['0.3141592653589793']
        # odrs2 = [odrs[1], odrs[2]]
        # newOdr = self.merger.merge2R2L(odrs2)
        # extensions.view_road(newOdr,os.path.join('..',self.configuration.get("esminipath")))
        # odrs = self.odrDic['0.3141592653589793']
        # odrs2 = [odrs[3], odrs[4]]
        # newOdr = self.merger.merge2R2L(odrs2)
        # extensions.view_road(newOdr,os.path.join('..',self.configuration.get("esminipath")))

    def test_merge2R2L2(self):
        
        odrList = []
        for angleOdrList in self.odrDic.values():
            odrList += angleOdrList

        numberOfOds = len(odrList)

        for _ in range(5):

            try:
                selectedOdrs = [odrList[np.random.choice(numberOfOds)], odrList[np.random.choice(numberOfOds)]]
                newOdr = self.merger.merge2R2L(selectedOdrs)
                extensions.view_road(newOdr,os.path.join('..',self.configuration.get("esminipath")))
            except:
                pass
            # extensions.save_road_image(newOdr,os.path.join('..',self.configuration.get("esminipath")))