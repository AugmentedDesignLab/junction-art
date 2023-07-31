import pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
from junctionart.library.Configuration import Configuration
from junctionart.junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
import junctionart.extensions, os

builder = JunctionBuilderFromPointsAndHeading(country=CountryCodes.US, laneWidth=3)
configuration = Configuration()

roadDefinition = [

            {'x': -30, 'y': 30, 'heading': 2, 'leftLane': 2, 'rightLane': 2, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.start},
            {'x':   0, 'y': 30, 'heading': 1,  'leftLane': 2, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {'x':   0, 'y':  0, 'heading': -1.5, 'leftLane': 1, 'rightLane': 1, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.end},
        ]
odr = builder.createIntersectionFromPointsWithRoadDefinition(odrID=0, firstRoadId=100, roadDefinition=roadDefinition, straightRoadLen=40, getAsOdr=True)
odr.write_xml()
print("done")