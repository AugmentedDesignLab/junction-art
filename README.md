# Junction Art
Procedural Generation of Intersections for HD Maps for Autonomous Vehicle Development and Test. It's built using [pyodrx](https://github.com/pyoscx/pyodrx) library. It generates road networks in [Open drive](https://www.asam.net/standards/detail/opendrive/) format. Detailed documentation with architecture can be found in the **docs* folder of the repository.

# Installation

**Steps**:
1. install dependencies
2. create config.yaml (instructions below)
3. create output folder (a folder called "output" in the root directory)

## Dependencies:

Python 3.7+

1. pyodrx (included with the project. No need to install)
2. dill
3. pyyaml
4. scipy, numpy, matplotlib, pytest, unittest
5. methodtools.
6. flask and jinja2 (for web-ui)
7. scikit-spatial
8. z3
9. seaborn

### Conda commands:

1. conda install dill
2. conda install -c anaconda pyyaml 
3. conda install -c anaconda scipy
4. conda install -c conda-forge matplotlib
5. conda install -c anaconda unittest2
6. conda install -c conda-forge scikit-spatial
7. conda install -c asmeurer z3 (optional for road generation)
8. conda install -c anaconda seaborn (for analysis)

## Configuration - create config.yaml
copy the contents of config-sample.yaml file and create a new file "config.yaml" in the root directory of the project. Now change these configurations:


1. esminipath - the folder containing the bin folder of esmini
2. rootPath - the path to the root folder of this project.


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





