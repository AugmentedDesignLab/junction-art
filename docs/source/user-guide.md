# User Manual

JunctionArt produces HD roadmaps and intersections. 


## Create intersection from incident points

In order to create an intersections using JunctionArt, there are some functionalities implemented in the **JunctionBuilderFromPointsAndHeading** class. Initialize the object **JunctionBuilderFromPointsAndHeading** using **CountryCode** and **laneWidth** for all the roads. Default country is US and the default width is three. 

First import the following modules.

:::{code-block}
import pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
from library.Configuration import Configuration
from junctionart.junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
import junctionart.extensions, os
:::

Create the **JunctionBuilderFromPointsAndHeading** object. A;so create the **configuration** object to fetch the directory of esmini **odr_viewer**. 

:::{code-block}
builder = JunctionBuilderFromPointsAndHeading(country=CountryCodes.US, laneWidth=3)
configuration = Configuration()
:::

Specificly, function **createIntersectionFromPointsWithRoadDefinition** takes in odr ID, road definition (described below), road ID for the first road, length of the defined straight roads,and the format of the output. If getAsOdr is false, the function returns an intersection object. 

:::{code-block}
odr = builder.createIntersectionFromPointsWithRoadDefinition(odrID=0, firstRoadId=100, roadDefinition=roadDefinition, straightRoadLen=40, getAsOdr=True)
:::

1. **odrID** = unique ID for the resultant OpenDRIVE file
2. **firstRoadId** = ID of the first road, ID of the rest of the roads are greater than **firstRoadId**
3. **roadDefinition** = List of dictionaries for defining the incident roads 
4. **straightRoadLen** = length of the defined straight roads. All the incident roads have the same length.
5. **getAsOdr** = a boolean to define othe output format. If **True** the output will an xodr file, otherwise the function returns an **Intersection** object. 


### Road Definition
Road definition is a list of dictionary to describe the incident roads of an intersection formatted as below:

:::{code-block}
roadDefinition = [

            {'x': -30, 'y': 30, 'heading': 2, 'leftLane': 2, 'rightLane': 2, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.start},
            {'x':   0, 'y': 30, 'heading': 1,  'leftLane': 2, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {'x':   0, 'y':  0, 'heading': -1.5, 'leftLane': 1, 'rightLane': 1, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.end},
        ]
:::

1. **x, y** is the cartesian coordinate of the point where the straight road is connected with the intersection. **heading** is the direction of the road outwards to the intersection. **heading** needs to be defined in **radians**. 

2. **leftLane** and **rightLane** define the number of lanes of the incident roads. 

3. **medianType** can takes the value **None/partial**. This parameter adds an island at the end of the road. Users can skip one end point by using the parameter **skipEndpoint** (possible values are **pyodrx.ContactPoint.start** and **pyodrx.ContactPoint.end**).

4. **Roads needs to be defined in clock-wise order**

To view the intersection generated by using the above-mentioned road definition use the following statement:

:::{code-block}
extensions.view_road(odr, os.path.join('..',configuration.get("esminipath"))) 
:::

![three way intersection](images/threeWay.png)





