# Sequential Junction Builder

## Builder specific parameters

These parameters change the overall shape and configuration for intersections. Some parameters need to be adjusted for specific purposes. User should create different builders for different purposes.

    minAngle=np.pi/10, #Minimum clockwise angle between two consecutive incident roads. If the randomly chosen angle is less than minAngle, it will be clamped to minAngle.
    straightRoadLen=10, #length of the incident roads. should be kept to 1 meter.
    probLongConnection=0.3, # probability of a long connection road in the first 180 degree.
    probMinAngle=0.5, #probability of two consecutive incident roads having the minimum angle
    maxConnectionLength=50, #maximum length of a connection road inside the intersection
    minConnectionLength=12, #minimum length of a connection road inside the intersection. To be used in case of equal angle intersections or specific purposes.
    random_seed=1 #For reproduction

The most advanced method: **createWithRandomLaneConfigurations**

## Core parameters

    straightRoadsPath, #Used when reusing previously created straight roads.
    odrId, #unique id for the resultnat road network
    maxNumberOfRoadsPerJunction, # number of roads
    maxLanePerSide=2, #maximum number of lanes on left or right. 2 means, there will be 4-lane roads sometimes.
    minLanePerSide=0, #set to 0 for single sided roads
    internalConnections=True, #internal connections are connections between non-consecurtive pairs of incident roads
    cp1=pyodrx.ContactPoint.end,  #contact point on the first incident road. Should be end.
    randomState=None, # to reset builder random state. Not recommendec. Builder wide random seed is recommended.
    internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY, 
    uTurnLanes=1, #number of U-turn lanes. 1 means first incoming lane from the median will be used. Currently supports 0 and 1.
    restrictedLanes=False, #Adds nice restricted lanes on the both side. Currently adds to all the roads. Mixing up is possible.
    equalAngles=False #Set to True if needed.

## Long connection roads:
Long connection roads are only added in the first 180 section, otherwise last road may overlap with the first one.

## equal-angle intersections:

Parameters to set:

**equalAngles**=True

### Considerations:
1. There is a relation between number of incident roads and minimum connection length. If the connection length is too small, roads will overlap. Some safe parameters

### numroads = 8

maxLanePerSide=2
probLongConnection=0.01
minConnectionLength=25

maxLanePerSide=3
probLongConnection=0.01
minConnectionLength=35

## Examples:

Tests: test/test_SequentialJunctionBuilder.py

**Equal angle coupled with long connection roads can yield nice clusters.