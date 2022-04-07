# Installation

You can use JunctionArt as an intersection and road generator, or you can use it as a library to build features upon. Both needs the package to be installed. You can install it from {ref}`the source<section-install-source>` or {ref}`the pypi package<section-install-pypi>`. To view the roads, you need a tool like esmini or Mathworks Roadrunner. Many of our test codes are integrated with esmini odrplot.

## Python version:
Works in python 3.7.9. There are some internal python library issues with 3.7.11.

**There are some libraries that may face permission errors. In such cases, run your terminal in administrator mode**

(section-install-source)=
## Installing from source

1. Clone the repository from *https://github.com/AugmentedDesignLab/junction-art*

2. Install poetry and conda
https://python-poetry.org/docs/ 
https://www.anaconda.com/

3. Go to the root folder of the junction-art. Create a new virtual environment with conda.

Run these commands in order

:::{code-block}

    poetry config virtualenvs.create false --local
    conda env update -f requirements.yml --prune
    pip install --upgrade pip
    conda install -c conda-forge shapely
    conda install -c conda-forge matplotlib
    conda install -c conda-forge tabulate
    conda install -c conda-forge psutil
    conda install -c conda-forge scikit-spatial
    poetry install
:::
OR 
:::{code-block}

    poetry config virtualenvs.create false --local
    pip install -r requirements-pip.txt
    pip install --upgrade pip
    conda install -c conda-forge shapely
    conda install -c conda-forge matplotlib
    conda install -c conda-forge tabulate
    conda install -c conda-forge psutil
    conda install -c conda-forge scikit-spatial
    poetry install
:::


If you are going to use the analysis tools, you need to make sure libgeos_c is installed (the conda install -c conda-forge shapely command should install it by default.)


### Option 1: Install via conda (recommended)
1. Activate or create a conda environment for the project with python 3.7+
2. Put the name of your environment in the first line of requirements.yml file (located in the root).

```
name: your_env_name
```

and run:

:::{code-block}
$ conda env update -f requirements.yml --prune
:::

:::{admonition} --prune
Remove **--prune** if you need the existing python packages installed in your environment.
:::


### Option 2: Install via pip

:::{code-block}
$ pip install -r requirements-pip.txt
:::

(section-install-pypi)=
## Installing from pypi

1. pip install junctionart..
2. Install https://trac.osgeo.org/osgeo4w/ for analysis tools
:::{note}
And here's a note with a colon fence!
:::

