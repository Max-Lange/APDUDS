"""Defining file for all plotting functions

This script requires that `matplotlib`, `numpy` and `pandas` be installed within the Python
environment you are running this script in.

This file contains the following major functions:

    * network_plotter - Creates a plot containing the nodes (as points)
     and the conduits (as lines)
    * voronoi_plotter - Creates a plot of the nodes of a network, and the
    subcatchment area polygons
    * height_contour_plotter - Creates a plot containing a network, and a filled in contour plot
    of the depth values of the nodes
    * diameter_map - Creates a plot of the conduits of a network, with the thickness of the lines
    corresponding to the relative diameter size
"""

from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame

def network_plotter(nodes: DataFrame, edges: DataFrame, subplot_number: int, numbered=False):
    """Plots the nodes and conduits for a network as points and lines respectivly

    Args:
        nodes (DataFrame): The node data for a network
        edges (DataFrame): The conduit data for a network
        subplot_number (int): Ax to plot to
    """

    axes = plt.subplot(subplot_number)
    plt.plot(nodes.x, nodes.y, "o")

    for _, line in edges.iterrows():
        x_coord = [nodes.at[int(line["from"]), "x"], nodes.at[int(line["to"]), "x"]]
        y_coord = [nodes.at[int(line["from"]), "y"], nodes.at[int(line["to"]), "y"]]
        plt.plot(x_coord, y_coord, "#1f77b4")

    if numbered:
        for index, node in nodes.iterrows():
            axes.annotate(str(index), xy=(node.x, node.y), color="k")

    axes.set_title("Initial Pipe Network")
    axes.set_xlabel("Longitudinal Size")
    axes.set_ylabel("Latitudinal Size")
    plt.axis('scaled')


def voronoi_plotter(nodes: DataFrame, voro, subplot_number: int):
    """Plot the nodes as points and the subcathment areas a colored polygons

    Args:
        nodes (DataFrame): The node data for a network
        voro (freud.locality.voronoi): freud voronoi instance containting polygon information
        subplot_number (int): Ax to plot to
    """

    axes = plt.subplot(subplot_number)
    points = np.array([[nodes.x[i], nodes.y[i], 0] for i in range(len(nodes))])

    voro.plot(ax=axes, color_by_sides=False)
    axes.scatter(points[:, 0], points[:, 1])

    axes.set_title("Subcatchment Area for each Node")
    plt.axis("scaled")


def height_contour_plotter(nodes: DataFrame, edges: DataFrame, subplot_number:int, fig):
    """Creates a subplot of a contourmap of the depth of the nodes, with the conduit
    network laid overtop.

    Args:
        nodes (DataFrame): The node data for a network
        edges (DataFrame): The conduit data for a network
        subplot_number (int): Ax to plot to
    """

    axes = plt.subplot(subplot_number)

    for _, node in nodes.iterrows():
        if node.role == "node":
            axes.plot(node.x, node.y, "bo")

    for _, line in edges.iterrows():
        x_coord = [nodes.at[int(line["from"]), "x"], nodes.at[int(line["to"]), "x"]]
        y_coord = [nodes.at[int(line["from"]), "y"], nodes.at[int(line["to"]), "y"]]
        plt.plot(x_coord, y_coord, "b")

    outfalls = nodes.index[nodes['role'] == "outfall"].tolist()
    for outfall in outfalls:
        # Special first case for adding a label
        if outfall == outfalls[0]:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv", label="Outfall")

        else:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv")

    overflows = nodes.index[nodes['role'] == "overflow"].tolist()
    for overflow in overflows:
        # Special first case for adding a label
        if overflow == overflows[0]:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^", label="Overflow")

        else:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^")

    # Add the colored contours
    x_coords = nodes.x[(nodes.role == "node") | (nodes.role == "outfall")]
    y_coords = nodes.y[(nodes.role == "node") | (nodes.role == "outfall")]
    depths = nodes.install_depth[(nodes.role == "node") | (nodes.role == "outfall")] - nodes.elevation[(nodes.role == "node") | (nodes.role == "outfall")]
    contourf = axes.tricontourf(x_coords, y_coords, depths)

    # Add extra points on the end to get a larger graph extent
    axes.scatter([nodes.x.min()-50, nodes.x.max()+50],
                 [nodes.y.min()-50, nodes.y.max()+50],
                 color="white")

    cbar = fig.colorbar(contourf, ax=axes)
    cbar.set_label("Depth below ground [m]")

    axes.set_title("Contour Map of the Needed Node Depth")
    axes.legend()
    plt.axis("scaled")


def diameter_map(nodes: DataFrame, edges: DataFrame, subplot_number:int):
    """Creates a subplot of the conduits of the system, with the line thickness corresponding to
    the diameter size.

    Args:
        nodes (DataFrame): The node data of a network
        edges (DataFrame): The conduit data of a network
        diam_list (list[float]): List of the viable diameters (in [m])
        subplot_number (int): Ax to plot to
    """

    axes = plt.subplot(subplot_number)
    scalar = edges.diameter.max()

    outfalls = nodes.index[nodes['role'] == "outfall"].tolist()
    outfalls.extend(nodes.index[nodes['role'] == "overflow"].tolist())
    for _, line in edges.iterrows():
        if line["from"] not in outfalls and line["to"] not in outfalls:
            x_coord = [nodes.at[int(line["from"]), "x"], nodes.at[int(line["to"]), "x"]]
            y_coord = [nodes.at[int(line["from"]), "y"], nodes.at[int(line["to"]), "y"]]
            plt.plot(x_coord, y_coord, "#1f77b4", linewidth=line["diameter"] * 8 / scalar)

    outfalls = nodes.index[nodes['role'] == "outfall"].tolist()
    for outfall in outfalls:
        # Special first case for adding a label
        if outfall == outfalls[0]:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv", label="Outfall")

        else:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv")

    overflows = nodes.index[nodes['role'] == "overflow"].tolist()
    for overflow in overflows:
        # Special first case for adding a label
        if overflow == overflows[0]:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^", label="Overflow")

        else:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^")


    axes.set_title("Relative Diameters of the Conduits")
    axes.legend()
    plt.axis("scaled")


def tester():
    """Only used for testin purposes"""
    print("The plotter script has run")


if __name__ == "__main__":
    tester()
