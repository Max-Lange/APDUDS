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
from osm_extractor import extractor, cleaner, splitter
from plotter import network_plotter, voronoi_plotter, height_contour_plotter
from terminal import greeting, step_2_input
from attribute_calculator import voronoi_area, flow_and_height_new, flow_amount, diameter_calc
from matplotlib import pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)


def step_1(coords: list[float], space: int):
    """Runs the first section of calculations (network generation),
    and also shows the resulting graphs of the newly created network

    Args:
        coords (list[float]): north, south, east and west coordinates of the wanted bounding box
        space (int): maximum allowable distance between intermediate gullies
    """

    nodes, edges = extractor(coords)
    filtered_nodes, filtered_edges = cleaner(nodes, edges)
    split_nodes, split_edges = splitter(filtered_nodes, filtered_edges, space)
    area_nodes, voro = voronoi_area(split_nodes)

    _ = plt.figure()
    # Create a plot for the downloaded road network
    network_plotter(filtered_nodes, filtered_edges, 221)
    # Create a plot for the split road network
    network_plotter(split_nodes, split_edges, 222)
    # Create a plot of the vornoi catchement areas
    voronoi_plotter(area_nodes, voro, 223)

    plt.show()

    return area_nodes, split_edges


def step_2(nodes, edges, settings: dict):
    """Runs the second section of the calculations, which constists of the
    attribute calculations. Also displays a number of graph to the user

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
        settings (dict): Input parameters for the calculations

    Returns:
        tuple[DataFrame, DataFrame]: Nodes and conduits with calculated and updated
        attributes
    """

    nodes, edges = flow_and_height_new(nodes, edges, settings)
    nodes, edges = flow_amount(nodes, edges, settings)
    edges = diameter_calc(edges, settings["diam_list"])

    _ = plt.figure()
    height_contour_plotter(nodes, edges, 111)

    plt.show()

    return nodes, edges


def main():
    """Running this function starts the software in its entirety
    """

    coords, space = greeting()
    nodes, edges = step_1(coords, space)
    settings = step_2_input()
    _, _ = step_2(nodes, edges, settings)


def tester():
    """Only used for testing
    """

    test_coords = [51.9293, 51.9207, 4.8378, 4.8176]
    test_space = 100

    nodes, edges = step_1(test_coords, test_space)

    print(nodes, edges)

    settings = {"outfall":36, "overflow":1, "min_depth":1.1, "min_slope":1/500,
                "rainfall": 70, "perc_inp": 70, "diam_list": [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]}

    nodes, edges  = step_2(nodes, edges, settings)
    print(nodes, edges)
    print(edges.diameter.max())


if __name__ == "__main__":
    tester()
