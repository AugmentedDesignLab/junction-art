import pytest
import pyodrx
import numpy as np

def test_link():
    link = pyodrx.links._Link('successor','1')
    
    pyodrx.prettyprint(link.get_element())

    link = pyodrx.links._Link('successor','1',element_type=pyodrx.ElementType.road,contact_point=pyodrx.ContactPoint.start)
    
    pyodrx.prettyprint(link.get_element())

def test_links():

    links = pyodrx.links._Links()
    pyodrx.prettyprint(links.get_element())
    link = pyodrx.links._Link('successor','1')
    links.add_link(link)    
    pyodrx.prettyprint(links.get_element())

def test_lanelinker():

    lane = pyodrx.Lane(a=3)
    lane._set_lane_id(1)
    lane.add_link('successor','2')

    pyodrx.prettyprint(lane.get_element())

def test_connection():
    con = pyodrx.Connection(1,2,pyodrx.ContactPoint.start,5)

    con.add_lanelink(1,-1)
    con.add_lanelink(2,-2)

    pyodrx.prettyprint(con.get_element())

def test_junction():
    con1 = pyodrx.Connection(1,2,pyodrx.ContactPoint.start)

    con1.add_lanelink(1,-1)
    con1.add_lanelink(2,-2)

    con2 = pyodrx.Connection(2,1,pyodrx.ContactPoint.start)

    con2.add_lanelink(1,-1)
    con2.add_lanelink(2,-2)
    con2.add_lanelink(3,-3)

    junciton = pyodrx.Junction('',1)

    junciton.add_connection(con1)
    junciton.add_connection(con2)

    pyodrx.prettyprint(junciton.get_element())


# road - road - road // -> - -> - -> 
def test_create_lane_links_normalroad1(): 

    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)

    geom= []
    geom.append(pyodrx.Line(50))
    geom.append(pyodrx.Arc(0.01,angle=np.pi/2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])      
    # create centerlanes
    for i in range(len(geom)):
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
    #add roadmarks 
    for i in range(len(geom)):
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
    # create lanesections
    for i in range(len(geom)):
        lanesec.append(pyodrx.LaneSection(0,lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
    #create lanes 
    for i in range(len(geom)):
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    #create roads 
    road1 = pyodrx.Road(1,planview[0],lanes[0])
    road1.add_successor(pyodrx.ElementType.road,2, pyodrx.ContactPoint.start)
     
    road2 = pyodrx.Road(2,planview[1],lanes[1])
    road2.add_predecessor(pyodrx.ElementType.road,1, pyodrx.ContactPoint.end)
    road2.add_successor(pyodrx.ElementType.road,3, pyodrx.ContactPoint.start)
     
    road3 = pyodrx.Road(3,planview[2],lanes[2])
    road3.add_predecessor(pyodrx.ElementType.road,2, pyodrx.ContactPoint.end)
     
    # create the opendrive and add roads 
    odr = pyodrx.OpenDrive('myroad')
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()
    
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert int(road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id() ) == -1
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() == None
    assert int(road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id() ) == 1

    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() ) == -1
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id() ) == -1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() ) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id() ) == 1

    assert int(road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() ) == -1
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id() == None
    assert int(road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() ) == 1
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id() == None


# road - junction - road // -> - -> - -> 
def test_create_lane_links_junction1(): 

    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)

    geom= []
    geom.append(pyodrx.Line(50))
    geom.append(pyodrx.Arc(0.01,angle=np.pi/2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])      
    # create centerlanes
    for i in range(len(geom)):
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
    #add roadmarks 
    for i in range(len(geom)):
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
    # create lanesections
    for i in range(len(geom)):
        lanesec.append(pyodrx.LaneSection(0,lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
    #create lanes 
    for i in range(len(geom)):
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    #create roads 
    road1 = pyodrx.Road(1,planview[0],lanes[0])
    road1.add_successor(pyodrx.ElementType.junction,1)
     
    road2 = pyodrx.Road(2,planview[1],lanes[1],road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)
    road2.add_successor(pyodrx.ElementType.road,3,pyodrx.ContactPoint.start)
     
    road3 = pyodrx.Road(3,planview[2],lanes[2])
    road3.add_predecessor(pyodrx.ElementType.junction,1)
     
    # create the opendrive and add roads 
    odr = pyodrx.OpenDrive('myroad')
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() ) == -1
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id() ) == -1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() ) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id() ) == 1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None

# road - junction - road // <- - -> - <- 
def test_create_lane_links_junction2(): 

    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)

    geom= []
    geom.append(pyodrx.Line(50))
    geom.append(pyodrx.Arc(0.01,angle=np.pi/2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])      
    # create centerlanes
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
    #add roadmarks 
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
    # create lanesections
        lanesec.append(pyodrx.LaneSection(0,lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
    #create lanes 
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    #create roads 
    road1 = pyodrx.Road(1,planview[0],lanes[0])
    road1.add_predecessor(pyodrx.ElementType.junction,1)
     
    road2 = pyodrx.Road(2,planview[1],lanes[1],road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.start)
    road2.add_successor(pyodrx.ElementType.road,3,pyodrx.ContactPoint.end)
     
    road3 = pyodrx.Road(3,planview[2],lanes[2])
    road3.add_successor(pyodrx.ElementType.junction,1)
     
    # create the opendrive and add roads 
    odr = pyodrx.OpenDrive('myroad')
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() ) == 1
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id() ) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() ) == -1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id() ) == -1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None

# road - junction - road // <- - -> - ->
def test_create_lane_links_junction3(): 

    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)

    geom= []
    geom.append(pyodrx.Line(50))
    geom.append(pyodrx.Arc(0.01,angle=np.pi/2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])      
    # create centerlanes
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
    #add roadmarks 
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
    # create lanesections
        lanesec.append(pyodrx.LaneSection(0,lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
    #create lanes 
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    #create roads 
    road1 = pyodrx.Road(1,planview[0],lanes[0])
    road1.add_predecessor(pyodrx.ElementType.junction,1)
     
    road2 = pyodrx.Road(2,planview[1],lanes[1],road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.start)
    road2.add_successor(pyodrx.ElementType.road,3,pyodrx.ContactPoint.start)
     
    road3 = pyodrx.Road(3,planview[2],lanes[2])
    road3.add_predecessor(pyodrx.ElementType.junction,1)
     
    # create the opendrive and add roads 
    odr = pyodrx.OpenDrive('myroad')
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() ) == 1
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id() ) == -1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() ) == -1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id() ) == 1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None

# road - junction - road // -> - -> - <-
def test_create_lane_links_junction4(): 

    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)

    geom= []
    geom.append(pyodrx.Line(50))
    geom.append(pyodrx.Arc(0.01,angle=np.pi/2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])      
    # create centerlanes
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
    #add roadmarks 
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
    # create lanesections
        lanesec.append(pyodrx.LaneSection(0,lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
    #create lanes 
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    #create roads 
    road1 = pyodrx.Road(1,planview[0],lanes[0])
    road1.add_successor(pyodrx.ElementType.junction,1)
     
    road2 = pyodrx.Road(2,planview[1],lanes[1],road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)
    road2.add_successor(pyodrx.ElementType.road,3,pyodrx.ContactPoint.end)
     
    road3 = pyodrx.Road(3,planview[2],lanes[2])
    road3.add_successor(pyodrx.ElementType.junction,1)
     
    # create the opendrive and add roads 
    odr = pyodrx.OpenDrive('myroad')
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() ) == -1
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id() ) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() ) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id() ) == -1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()  == None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id()  == None




