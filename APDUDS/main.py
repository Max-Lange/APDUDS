"""Main working / connecting file of APDUDS

This script connects all the seperate modules into the full program,
this script should be run if you want the program to start

This script requires that `matplotlib and warnings` be installed within the Python
environment you are running this script in. As well as all the packages required
by the modules 'osm_extractor', 'plotter' and 'terminal'.

This file contains the following modules:

    * step_1 - Runs the first section of calculations, and shows the resulting graphs
    * main - All the functions for the program to work in its entirety, is run when this
    script is run
    * tester - Only used for testing
"""

import warnings
from osm_extractor import extractor, splitter
from plotter import network_plotter
from terminal import greeting
from matplotlib import pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)


def step_1(coords: list[float], space: int):
    """Runs the first section of calculations (network generation),
    and also shows the resulting graphs of the newly created network

    Args:
        coords (list[float]): north, south, east and west coordinates of the wanted bounding box
        space (int): maximum allowable distance between intermediate gullies
    """
    nodes_1, edges_1 = extractor(coords)
    nodes_2, edges_2 = splitter(nodes_1, edges_1, space)

    _ = plt.figure()
    # Create a plot for the downloaded road network
    network_plotter(nodes_1, edges_1, subplot_number=121)
    # Create a plot for the split road network
    network_plotter(nodes_2, edges_2, subplot_number=122)

    plt.show()



def main():
    """Running this function starts the software in its entirety
    """

    coords, space = greeting()
    step_1(coords, space)



def tester():
    """Only used for testing
    """

    test_coords = [51.9293, 51.9207, 4.8378, 4.8176]
    test_space = 50

    step_1(test_coords, test_space)

if __name__ == "__main__":
    tester()
