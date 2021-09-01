import os
import re
from pytest import fixture
from junctionart.library.Configuration import Configuration


@fixture
def config():
    return Configuration()

@fixture
def outputDir():
    return os.path.join(os.getcwd(), 'output')


@fixture
def esminiPath(config):
    return config.get("esminipath")