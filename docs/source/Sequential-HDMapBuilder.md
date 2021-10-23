## Sequential HD Map Builder

1. A collection of intersections, curves into unplaced segments
2. A collection of road segments(no intersection) into unplaced connection roads
3. Loop:
1.1. A Blank map with grid cells, 1.x1 meter cells.
1.2. Place the first intersection in the center of the map. Fill the occupied cells.
1.3. Update the list of open slots and 
1.4. Choose a slot. Find a segment that can be connected to the slot without overlapping with any other segments in the map with a distance between (min, max). This would be a grid search. If no such candidates. End this loop. A scoring system for connecting to more slots?
1.5. So, now we have a location on the map for the new intersection. Rotate the intersection so that a matching incident road has the same heading as the chosen slot.
1.6. Connect the slot with the incident point with a straight road. Transform the new intersection and fill the cells for both the straight road and new intersection.
1.7. Connect 50% of the incident roads of the new intersection with existing slots without creating an overlap and a lot of curve. (This needs some greedy approach, otherwise it would be very slow). Maybe another grid search within a box.
1.8  update open slots.

Dynamic cell groups:

Each segment has a cell group. If we want to find the segment on the left. We need to find the group on the left.  The group on the left can be bigger or smaller. How can we search efficiently?

When we fill the cell, we can store, segment ref, group ref.

So, it's more like ray tracing. from a point. we trace cells in a direction. Before a placement, the bounding box must completely fill into a place without filled cells. Gap constraints?