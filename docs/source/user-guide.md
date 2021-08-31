# User Manual

JunctionArt produces HD roadmaps and intersections. 


## Create intersection from incident points

In order to create an intersections using JunctionArt, there are some functionalities implemented in the **JunctionBuilderFromPointsAndHeading** class. Initialize the object **JunctionBuilderFromPointsAndHeading** using **CountryCode** and **laneWidth** for all the roads. Default country is US and the default width is three. 

:::{code-block}
builder = JunctionBuilderFromPointsAndHeading(country=CountryCodes.US, laneWidth=3)
:::

Specificly, function **createIntersectionFromPointsWithRoadDefinition** takes in odr ID, road definition (described below), road ID for the first road, length of the defined straight roads,and the format of the output. If getAsOdr is false, the function returns an intersection object. 

:::{code-block}
odr = builder.createIntersectionFromPointsWithRoadDefinition(odrID=0, firstRoadId=100, roadDefinition=roadDefinition, firstRoadId=10, straightRoadLen=40, getAsOdr=True)
:::

### Road Definition
Road definition is a list of dictionary to describe the incident roads of an intersection formatted as below:

:::{code-block}
roadDefinition = [
            {'x': -30, 'y': 30, 'heading': 2, 'leftLane': 3, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None},
            {'x':   0, 'y': 30, 'heading': 1,  'leftLane': 3, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {'x':   0, 'y':  0, 'heading': -1.5, 'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None}
            ]
:::

Median type can takes the value **None/partial**. This parameter adds an island at the end of the road. User can skip one end point by using the parameter **skipEndpoint**. 





