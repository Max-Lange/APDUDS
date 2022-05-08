"""Defining file for all the attribute calculation functions

This script defines the functions that calculate certain attributes of the network,
such as the catchment area, as well as the elevation

This script requires that `freud, numpy and pandas` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:s

    * voronoi_area - Calculates the catchment area for each node using voronoi
    * main - Only used for testing purposes
"""

import pandas as pd
from freud.box import Box
from freud.locality import Voronoi
import numpy as np

def voronoi_area(nodes: pd.DataFrame, box_extent: int = 10):
    """_summary_

    Args:
        nodes (pd.DataFrame): x and y positions of all the nodes
        box_extent (int, optional): area to extend the bounding box by. Defaults to 10.

    Returns:
        tuple([pd.DataFrame, Freud.locality.Voronoi]): nodes with a catchment area column added,
        and completed vornoir calculation (for plotting purposes)
    """

    nodes = nodes.copy()

    box_length_x = nodes.x.max() * 2 + box_extent * 2
    box_length_y = nodes.y.max() * 2 + box_extent * 2

    box = Box(Lx=box_length_x, Ly=box_length_y, is2D=True)
    points = np.array([[nodes.x[i], nodes.y[i], 0] for i in range(len(nodes))])

    voro = Voronoi()
    voro.compute((box, points))

    nodes["catchment"] = voro.volumes

    return nodes, voro


def main():
    """Only used for testing purposes
    """
    # nodes = pd.read_csv("test_nodes_2.csv")

    # voronoi_area(nodes, box_extent=50)


if __name__ == "__main__":
    main()
