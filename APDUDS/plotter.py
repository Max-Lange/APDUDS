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
from pandas import DataFrame

def network_plotter(nodes: DataFrame, edges: DataFrame, subplot_number: int):
    """Plots the nodes and edges for the given network

    Args:
        nodes (DataFrame): positional (x, y) data of the nodes
        edges (DataFrame): from, to data of the edges
        relevant_ax (bool, optional): Ax to plot to (use if you want the plot
        to be part of an external subplot). Defaults to None.
    """
    plt.subplot(subplot_number)
    plt.plot(nodes.x, nodes.y, "o")
    for index, line in edges.iterrows():
        style = ["solid", "dashed", "dashdot", "dotted"]
        x_coord = [nodes.iloc[int(line["from"])]["x"], nodes.iloc[int(line["to"])]["x"]]
        y_coord = [nodes.iloc[int(line["from"])]["y"], nodes.iloc[int(line["to"])]["y"]]
        plt.plot(x_coord, y_coord, linestyle=style[index % 4])


    plt.axis('scaled')
