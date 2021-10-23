from hypernet.devtools import *
from junctionart.library.Configuration import Configuration

def test_import():
    import_submodules('junctionart.junctions')
    import_submodules('junctionart.extensions')
    import_submodules('junctionart.roadgen')


def test_config():

    config = Configuration()
    assert config.get("esminipath") is not None
    # assert False
