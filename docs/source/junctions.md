# Keypoints

1. The successor or predecessor of an incident road is a junction object, not a road object.
2. For each incident road, we are creating a set of connection roads from its incoming lanes. So, in the juncttion description, these connection roads need to be included. The data we need here are: laneConfigurations, contact points between the incoming road and connection road, lane links of the incoming road and the connection road.
3. Now, we need a builder, that can take all this input and build the junction.

Steps for the builder:
1. take junction id, outside roads and connection road as inputs
2. For each connection road, if it's successor or predecessor is an incident road:
    a. create a junction object
    a. set incident roads junction id and type
    b. add the link to the junction object