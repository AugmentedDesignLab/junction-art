# Junction Art
A library to harvest different kinds of road junctions. It's built using [pyodrx](https://github.com/pyoscx/pyodrx) library. It generates road networks in [Open drive](https://www.asam.net/standards/detail/opendrive/) format.

# Dependencies:

1. pyodrx (included with the project. No need to install)
2. dill
3. pyyaml
4. scipy, numpy, matplotlib, pytest, unittest

# Configuration

1. esminipath
2. esmini resources folder
3. notebook path


# Conventions:

1. successor is connected to one's end.
2. predecessor is connected to one's start.

# JunctionHarvester
This is the class that harvests junctions. 

# Common use-cases:

## 2 roads 2 lanes: harvest2ways2Lanes

## 3 roads from 2 roads: harvest3WayJunctionsFrom2Ways


