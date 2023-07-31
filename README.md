# Junction Art
Procedural Generation of Intersections for HD Maps for Autonomous Vehicle Development and Test. It's built using [pyodrx](https://github.com/pyoscx/pyodrx) library. It generates road networks in [Open drive](https://www.asam.net/standards/detail/opendrive/) format. Detailed documentation with architecture can be found in the **docs* folder of the repository.

**The documentation moved to [https://junctionart.readthedocs.io/](https://junctionart.readthedocs.io/)**

## Citations

We have two peer-review papers and one preprint in this project. Please, cite the one that's most relevant to your research.

### 1. HD Road Generation - complete city like maps

```
@article{Muktadir2022ProceduralGO,
    author = {Muktadir, Golam Md and Jawad, Abdul and Paranjape, Ishaan and Whitehead, Jim and Shepelev, Aleksey},
    year = {2022},
    month = {05},
    pages = {22},
    title = {Procedural Generation of High-Definition Road Networks for Autonomous Vehicle Testing and Traffic Simulations},
    volume = {6},
    journal = {SAE International Journal of Connected and Automated Vehicles},
    doi = {10.4271/12-06-01-0007}
}
```

### 2. Roundabout Generation - classic and turbo roundabouts

```
@INPROCEEDINGS{10186533,
    author={Ikram, Zarif and Muktadir, Golam Md and Whitehead, Jim},
    booktitle={2023 IEEE Intelligent Vehicles Symposium (IV)}, 
    title={Procedural Generation of Complex Roundabouts for Autonomous Vehicle Testing}, 
    year={2023},
    volume={},
    number={},
    pages={1-6},
    doi={10.1109/IV55152.2023.10186533}
}
```


### 3. Intersection Generation - most expressive intersection generator today


```
@unknown{Muktadir2022Intersections,
    author = {Muktadir, Golam Md and Jawad, Abdul and Shepelev, Aleksey and Paranjape, Ishaan and Whitehead, Jim},
    year = {2022},
    month = {05},
    pages = {},
    title = {P r e -P r i n t Realistic Road Generation: Intersections},
    doi = {10.13140/RG.2.2.30541.51683}
}
```

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
10. shapely, (requres installation of [osgeo](https://stackoverflow.com/questions/12578471/oserror-geos-c-could-not-be-found-when-installing-shapely/50623996#50623996)
11. pandas
12. tqdm
13. sympy
14. geos

### Conda commands:

1. conda install dill
2. conda install -c anaconda pyyaml 
3. conda install -c anaconda scipy
4. conda install -c conda-forge matplotlib
5. conda install -c anaconda unittest2
6. conda install -c conda-forge scikit-spatial
7. conda install -c asmeurer z3 (optional for road generation)
8. conda install -c anaconda seaborn (for analysis)
9. conda install -c conda-forge shapely 
10. conda install -c conda-forge pandas 
11. conda install tqdm 
12. conda install -c conda-forge shapely 
13. conda install -c conda-forge geos


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





