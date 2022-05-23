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
    # style = ["solid", "dashed", "dashdot", "dotted"]
    for _, line in edges.iterrows():
        x_coord = [nodes.at[int(line["from"]), "x"], nodes.at[int(line["to"]), "x"]]
        y_coord = [nodes.at[int(line["from"]), "y"], nodes.at[int(line["to"]), "y"]]
        # plt.plot(x_coord, y_coord, linestyle=style[index % 4])
        plt.plot(x_coord, y_coord, "#1f77b4")

    if numbered:
        for index, node in nodes.iterrows():
            axes.annotate(str(index), xy=(node.x, node.y), color="k")

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
    voro.plot(ax=axes)
    axes.scatter(points[:, 0], points[:, 1])


def height_contour_plotter(nodes: DataFrame, edges: DataFrame, subplot_number:int):
    """Creates a subplot of a contourmap of the depth of the nodes, with the conduit
    network laid overtop.

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
        subplot_number (int): Ax to plot to
    """

    axes = plt.subplot(subplot_number)

    axes.plot(nodes.x, nodes.y, 'bo')

    outfall = nodes.index[nodes['role'] == "outfall"].tolist()[0]
    overflow = nodes.index[nodes['role'] == "overflow"].tolist()[0]

    for _, line in edges.iterrows():
        x_coord = [nodes.at[int(line["from"]), "x"], nodes.at[int(line["to"]), "x"]]
        y_coord = [nodes.at[int(line["from"]), "y"], nodes.at[int(line["to"]), "y"]]
        plt.plot(x_coord, y_coord, "b")

    axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "ro")
    axes.plot(nodes.at[overflow, "x"], nodes.at[overflow, "y"], "ro")

    axes.tricontourf(nodes.x, nodes.y, nodes.depth)
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

    for _, line in edges.iterrows():
        x_coord = [nodes.at[int(line["from"]), "x"], nodes.at[int(line["to"]), "x"]]
        y_coord = [nodes.at[int(line["from"]), "y"], nodes.at[int(line["to"]), "y"]]
        plt.plot(x_coord, y_coord, "#1f77b4", linewidth=line["diameter"] * 8 / scalar)

    outfall = nodes.index[nodes['role'] == "outfall"].tolist()[0]
    axes.plot(nodes.at[outfall, "x"], nodes.at[outfall, "y"], "ro")

    plt.axis("scaled")
