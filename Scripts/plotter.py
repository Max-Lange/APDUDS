"""Defining file for all plotting functions

This script defines the functions that facilitate the creations of all the different kinds
of plots that are needed by the program.

This script requires that `matplotlib and pandas` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:s

    * network_plotter - Creates a graph containing the nodes as points and the edges as lines
"""

from matplotlib import pyplot as plt
import numpy as np
from pandas import DataFrame

def network_plotter(nodes: DataFrame, edges: DataFrame, subplot_number: int, numbered=False):
    """Plots the nodes and edges for the given network

    Args:
        nodes (DataFrame): positional (x, y) data of the nodes
        edges (DataFrame): from, to data of the edges
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
    """Fill a plot with the nodes as points and the vornoi areas a colored polygons

    Args:
        nodes (DataFrame): x and y positions of the nodes
        voro (freud.locality.voronoi): freud voronoi instance containting polygon information
        subplot_number (int): Ax to plot to
    """

    points = np.array([[nodes.x[i], nodes.y[i], 0] for i in range(len(nodes))])

    axes = plt.subplot(subplot_number)
    voro.plot(ax=axes, color_by_sides=False)
    axes.scatter(points[:, 0], points[:, 1])

    axes.set_title("Subcatchment Area for each Node")
    plt.axis("scaled")


def height_contour_plotter(nodes: DataFrame, edges: DataFrame, subplot_number:int, fig):
    """Creates a subplot of a contourmap of the depth of the nodes, with the conduit
    network laid overtop.

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
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
        if outfall == outfalls[0]:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv", label="Outfall")

        else:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv")

    overflows = nodes.index[nodes['role'] == "overflow"].tolist()
    for overflow in overflows:
        if overflow == overflows[0]:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^", label="Overflow")

        else:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^")

    x_coords = nodes.x[(nodes.role == "node") | (nodes.role == "outfall")]
    y_coords = nodes.y[(nodes.role == "node") | (nodes.role == "outfall")]
    depths = nodes.depth[(nodes.role == "node") | (nodes.role == "outfall")]
    contourf = axes.tricontourf(x_coords, y_coords, depths)

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
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
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
        if outfall == outfalls[0]:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv", label="Outfall")

        else:
            axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "rv")

    overflows = nodes.index[nodes['role'] == "overflow"].tolist()
    for overflow in overflows:
        if overflow == overflows[0]:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^", label="Overflow")

        else:
            axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "r^")


    axes.set_title("Relative Diameters of the Conduits")
    axes.legend()
    plt.axis("scaled")
