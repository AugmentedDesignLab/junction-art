# Strategies for lane configurations

Two roads with different lane configurations can be connected by a connection road. There are may ways this connection road can be created. Connection roads can connect all the lanes or some of them.

Basic steps:

 1. Create all the roads
 2. Drop all the lanes from the connection roads and rebuild the lanes.




## Intersections

## Non-intersections (2-roads only)

### With new connection road strategies:
In case of two roads, they are connected by a middle road if they have different lane configurations.

#### Merge at edge
Lanes closer to the median are connected first. Lanes at the edges are merged if there are no unique relationships possible. This is useful when roads are not already placed on inertial system.


    LaneBuilder::createLanesForConnectionRoad

#### Merge by distance:

This is useful when roads alreay have fixed intertial co-ordinates. A pair of lanes having lower distance is connected before a pair with higher distance. When no unique relationships are possible, create merge lanes. We can start by finding the predecessor lanes to the reference line which are cloest. It has many corner cases and produces lane crossings which leads to unsafe paths.

#### Merge at median:

Opposite of Merge at edge. Pretty useful if edges are closer than medians.


#### Merge in the middle:

1. Connect (-1, -1)
2. Connect (-edge1, -edge2)
3. for each un connected lane, if no unique relationship, merge based on the distances from edge and median.