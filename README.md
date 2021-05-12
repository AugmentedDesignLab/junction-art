# Junction Art
Procedural Generation of Intersections for HD Maps for Autonomous Vehicle Development and Test. It's built using [pyodrx](https://github.com/pyoscx/pyodrx) library. It generates road networks in [Open drive](https://www.asam.net/standards/detail/opendrive/) format. Detailed documentation with architecture can be found in the **docs* folder of the repository.

# Dependencies:

1. pyodrx (included with the project. No need to install)
2. dill
3. pyyaml
4. scipy, numpy, matplotlib, pytest, unittest
5. methodtools.
6. flask and jinja2 (for web-ui)

# Configuration

1. esminipath
2. esmini resources folder
3. notebook path


# Conventions:

1. successor is connected to one's end.
2. predecessor is connected to one's start.


# Immutable objects: (recreate instead of edits because they are shared amount different users)
1. raw geometries in planview (Line, Arc, Spiral, ParamPoly, etc.)
2. any lane
3. any link

# API

## Road Generators:
Documentation: [Road Generators](https://github.com/AugmentedDesignLab/junction-art/wiki/Road-Generators)

## SequentialJunctionBuilder

Detailed documentation: [docs/Sequential-RoadBuilder.md](docs/Sequential-RoadBuilder.md)

## JunctionHarvester
This is the class that harvests junctions. 

## Common use-cases:

### 2 roads 2 lanes: harvest2ways2Lanes

### 3 roads from 2 roads: harvest3WayJunctionsFrom2Ways





