# Installation

You can use JunctionArt as an intersection and road generator, or you can use it as a library to build features upon. Both needs the package to be installed. You can install it from {ref}`the source<section-install-source>` or {ref}`the pypi package<section-install-pypi>`. To view the roads, you need a tool like esmini or Mathworks Roadrunner. Many of our test codes are integrated with esmini odrplot.


(section-install-source)=
## Installing from source

## Installing from source2

1. Clone the repository from *https://github.com/AugmentedDesignLab/junction-art*
2. Install it from the root folder of the project.


### Option 1: Install via conda (recommended)
Activate or create a conda environment for the project and run:

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


:::{note}
And here's a note with a colon fence!
:::
