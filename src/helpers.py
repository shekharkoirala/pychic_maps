import osmnx as ox

def check_ox_version():
    assert ox.__version__[0] == "2"
