import logging
from .fixtures import *

import junctionart.extensions as extensions
from junctionart.roadgen.controlLine.ControlLineBasedGenerator import ControlLineBasedGenerator

logfile = 'ControlLineBasedGenerator.log'
with open(logfile, 'w') as f:
    f.truncate()
logging.basicConfig(level=logging.INFO, filename=logfile)


def test_A(esminiPath):
    generator = ControlLineBasedGenerator((400, 400), debug=True, seed=1, randomizeHeading=True, randomizeDistance=False, nLaneDistributionOnASide=[0.2, 0.7, 0.1, 0], nLaneDistributionOnControlLines=[0, 0.2, 0.7, 0.1])

    for _ in range(2):
        odr = generator.generateWithManualControlines("test_mapA", layout='A', plotGrid=False)

        # xmlPath = f"output/test_generateWithManualControlLines2.xodr"
        # odr.write_xml(xmlPath)
        extensions.view_road(odr, os.path.join('..', esminiPath)) 