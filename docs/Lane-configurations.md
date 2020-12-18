# Strategies for lane configurations

## Intersections

## Non-intersections (2-roads only)

### With new connection road strategies:
In case of two roads, they are connected by a middle road if they have different lane configurations.

#### Merge at edge
Lanes closer to the median are connected first. Lanes at the edges are merged if there are no unique relationships possible. This is useful when roads are not already placed on inertial system.

#### Merge by distance:

This is useful when roads alreay have fixed intertial co-ordinates. A pair of lanes having lower distance is connected before a pair with higher distance. When no unique relationships are possible, create merge lanes. We can start by finding the predecessor lanes to the reference line which are cloest. It has many corner cases and produces lane crossings which leads to unsafe paths.

#### Merge at median:

Opposite of Merge at edge. Pretty useful if edges are closer than medians.


#### Merge in the middle:

1. Connect (-1, -1)
2. Connect (-edge1, -edge2)
3. for each un connected lane, if no unique relationship, merge based on the distances from edge and median.