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

import networkx as nx
import pandas as pd
from freud.box import Box
from freud.locality import Voronoi
import numpy as np

def voronoi_area(nodes: pd.DataFrame, box_extent: int=10):
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

    nodes["area"] = voro.volumes

    return nodes, voro

def flow_and_height(nodes: pd.DataFrame, edges: pd.DataFrame, settings:dict):
    """Determines the direction of flow and needed installation height of the nodes based
    on the given settings (minimum slope, minimum depth and position of the outfall node)

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
        settings (dict): Values for the minimum slope, the minimum depth, and locations
        of the outfall and overflow points

    Returns:
        tuple[DataFrame, DataFrame]: The nodes and conduits dataframes with the newly determined
        flow direction and needed installation depth of the nodes
    """

    nodes = nodes.copy()
    edges = edges.copy()

    nodes, edges, graph = intialize(nodes, edges, settings)
    end_points = settings["outfalls"]
    nodes.loc[end_points, "considered"] = True
    edge_set = [set([edges["from"][i], edges["to"][i]]) for i in range(len(edges))]

    i = 1
    while not nodes["considered"].all():
        leaf_nodes = nodes.index[nodes.connections == i].tolist()

        for node in leaf_nodes:
            if not nodes.at[node, "considered"]:
                path = determine_path(graph, node, end_points)
                nodes = set_paths(nodes, path)
                nodes = set_depth(nodes, edges, path, settings["min_slope"], edge_set)

                nodes.loc[path, "considered"] = True
        i += 1

    if "max_slope" in settings:
        nodes = uphold_max_slope(nodes, edges, edge_set, settings["max_slope"])

    edges = reset_direction(nodes, edges)
    return nodes, edges


def intialize(nodes: pd.DataFrame, edges: pd.DataFrame, settings: dict):
    """_summary_

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
        settings (dict): values for the minimum depth and the positions of the
        outfall and overflow points

    Returns:
        tuple[DataFrame, DataFrame, Graph]: The nodes and edges dataframes with
        new columns which are needed (or will be filled in) in the later functions
        of the flow direction and depth calculation process. Also a NetworkX Graph
        for calculating the shortest paths using networkx' dijkstra function
    """

    nodes["considered"] = False
    nodes["depth"] = settings["min_depth"]
    nodes["role"] = "node"
    nodes["path"] = None

    ruined_edges = edges.copy()
    edges_melted = ruined_edges[["from", "to"]].melt(var_name='columns', value_name='index')
    edges_melted["index"] = edges_melted["index"].astype(int)
    nodes["connections"] = edges_melted["index"].value_counts().sort_index()

    graph = nx.Graph()
    graph.add_nodes_from(list(nodes.index.values))

    for _, edge in edges.iterrows():
        graph.add_edge(edge["from"], edge["to"], weight=edge["length"])

    return nodes, edges, graph


def determine_path(graph: nx.Graph, start: int, ends: list[int]):
    """Determines the shortest path for a certain point to another point using
    Dijkstra's shortes path algorithm

    Args:
        graph (Graph): A NetworkX Graph object of the system
        start (int): The index of the starting node
        end (int): The index of the end node

    Returns:
        list[int]: The indicies of the nodes which the shortes path passes through
    """
    shortest_length = np.inf
    best_path = []

    for end_point in ends:
        length, path = nx.single_source_dijkstra(graph, start, target=end_point)

        if length < shortest_length:
            best_path = path
            shortest_length = length

    return [int(x) for x in best_path]


def set_paths(nodes: pd.DataFrame, path: list):
    """Determines the path to the end node for all the nodes along a given path

    Args:
        nodes (DataFrame): _description_
        path (list[int]): The indicies of the nodes which the path passes through

    Returns:
        DataFrame: Nodes data with the updated path for the relevant nodes
    """

    for i, node in enumerate(path):

        if not nodes.loc[node, "path"]:
            nodes.at[node, "path"] = path[i:]

    return nodes


def set_depth(nodes: pd.DataFrame, edges: pd.DataFrame,
path: list, min_slope: float, edge_set: list[set[int]]):
    """Set the depth of the nodes along a certain route using the given minimum slope.
    It calculates the distance between the nodes using conduit lenghts, and lowers the end
    point such that it satisfies the minimum slope.

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
        path (list): All the indicies of the nodes which the path passes through
        (including start and end nodes)
        min_slope (float): The value (1/distance [m]) for the minimum slope

    Returns:
        DataFrame: The nodes dataframe with updated depths for the nodes along the given path
    """

    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i+1]

        from_depth = nodes.at[from_node, "depth"]
        length = edges.at[edge_set.index(set([from_node, to_node])), "length"]
        new_to_depth = from_depth + min_slope * length

        if new_to_depth > nodes.at[to_node, "depth"]:
            nodes.at[to_node, "depth"] = new_to_depth

    return nodes

def uphold_max_slope(nodes, edges, edge_set, max_slope):
    """_summary_

    Args:
        nodes (_type_): _description_
        max_slope (_type_): _description_

    Returns:
        _type_: _description_
    """

    for _, node in nodes.iterrows():
        path = node.path

        for i in range(len(path)-1):
            lower_node = path[-1-i]
            higher_node = path[-2-i]
            length = edges.at[edge_set.index(set([lower_node, higher_node])), "length"]

            if nodes.at[lower_node, "depth"] - nodes.at[higher_node, "depth"] / length > max_slope:
                nodes.at[higher_node, "depth"] = nodes.at[lower_node, "depth"] - length * max_slope

    return nodes


def reset_direction(nodes: pd.DataFrame, edges: pd.DataFrame):
    """Flips the "from" and "to" columns for all conduits where necessary.

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes

    Returns:
        DataFrame: Edges data with the "from" "to" order corrected according to the depth
    """

    for i, edge in edges.iterrows():
        if nodes.at[edge["from"], "depth"] > nodes.at[edge["to"], "depth"]:
            edges.at[i, "from"], edges.at[i, "to"] = edge["to"], edge["from"]

    return edges


def flow_amount(nodes: pd.DataFrame, edges: pd.DataFrame, settings: dict):
    """Calculates the amount of flow throught the conduits based on the given design storm
    rainfall and the percentage of hardend ground surface.

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
        settings (dict): Values for the design storm rainfall and the percentage of hardend
        ground surface

    Returns:
        tuple[DataFrame, DataFrame]: nodes and conduits data with added inflow and flow rates
        for the nodes and conduits respectively
    """

    nodes = nodes.copy()
    edges = edges.copy()

    nodes["inflow"] = inflow(nodes, settings)
    edges["flow"] = 0
    edge_set = [set([edges["from"][i], edges["to"][i]]) for i in range(len(edges))]

    for _, node in nodes.iterrows():
        path = node["path"]

        # Can this not be simplified to a generator expression and a .loc?
        for j in range(len(path)-1):
            edge = set([path[j], path[j+1]])

            edges.at[edge_set.index(edge), "flow"] += node["inflow"]

    return nodes, edges


def inflow(nodes: pd.DataFrame, settings: dict):
    """Calculates the inflow amount for all nodes

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        settings (dict): Values for the design storm rainfall and the percentage of hardend
        ground surface

    Returns:
        DataFrame: nodes data with added inflow rates
    """

    return nodes["area"] * (settings["rainfall"] / (10**7)) * (settings["perc_inp"] / 100)


def diameter_calc(edges: pd.DataFrame, diam_list: list[float]):
    """Calculates the closest needed diameter (rounded up) for the given flow rate
    out of the given diameter list

    Args:
        edges (DataFrame): The conduits of the system along with their attributes
        diam_list (list[float]): List of the different usable diameter sizes for the
        conduits (in meters)

    Returns:
        DataFrame: Edges data with added diameters
    """

    edges["diameter"] = None

    for i, flow in enumerate(edges["flow"]):
        if flow == 0:
            edges.at[i, "diameter"] = diam_list[0]

        else:
            precise_diam = 2 * np.sqrt(flow / np.pi)

            if precise_diam > diam_list[-1]:
                edges.at[i, "diameter"] = diam_list[-1]

            else:
                for j, size in enumerate(diam_list):
                    if size - precise_diam > 0:
                        edges.at[i, "diameter"] = diam_list[j]

                        break

    return edges


def cleaner_and_trimmer(nodes: pd.DataFrame, edges: pd.DataFrame):
    """Round of calculated values to realistic decimal precisions, and drop columns
    which were added for intermediate calculations

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes

    Returns:
        tuple[DataFrame, DataFrame]: Cleaned up nodes and edges data
    """

    nodes = nodes.drop(columns=["considered", "path", "connections"])

    if "Unnamed: 0" in nodes.keys():
        nodes = nodes.drop(columns=["Unnamed: 0"])
        edges = edges.drop(columns=["Unnamed: 0"])

    # cm precision for x, y and depth
    # m^2 precision for area
    # L precision for inflow
    nodes.x = nodes.x.round(decimals=2)
    nodes.y = nodes.y.round(decimals=2)
    nodes.area = nodes.area.round(decimals=0)
    nodes.depth = nodes.depth.round(decimals=2)
    nodes.inflow = nodes.inflow.round(decimals=3)

    # cm precision for length
    # L precision for flow
    edges.length = edges.length.round(decimals=2)
    edges.flow = edges.flow.round(decimals=3)

    # Drop the conduits with 0 flow
    edges = edges[edges.flow != 0]
    edges = edges.reset_index(drop=True)

    return nodes, edges


def add_outfalls(nodes, edges, settings):

    for outfall in settings["outfalls"]:
        new_index = len(nodes)
        nodes.loc[new_index] = [nodes.at[outfall, "x"] + 1,
                                nodes.at[outfall, "y"] + 1,
                                0,
                                nodes.depth.max(),
                                "outfall",
                                0]

        edges.loc[len(edges)] = [outfall,
                                 new_index,
                                 1,
                                 0,
                                 settings["diam_list"][-1]]

    for overflow in settings["overflows"]:
        new_index = len(nodes)
        nodes.loc[new_index] = [nodes.at[overflow, "x"] + 1,
                                nodes.at[overflow, "y"] + 1,
                                0,
                                settings["min_depth"],
                                "overflow",
                                0]

        edges.loc[len(edges)] = [new_index,
                                 overflow,
                                 1,
                                 0,
                                 settings["diam_list"][-1]]

    return nodes, edges


def tester():
    """Only used for testing purposes
    """
    from matplotlib import pyplot as plt
    from plotter import height_contour_plotter, diameter_map
    nodes = pd.read_csv("test_nodes_2.csv")
    edges = pd.read_csv("test_edges_2.csv")
    settings = {"outfalls":[86], "overflows":[1, 2, 3], "min_depth":1.1, "min_slope":1/500,
                "rainfall": 70, "perc_inp": 25, "max_slope": 1/400,
                "diam_list": [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3]}

    nodes, _ = voronoi_area(nodes, box_extent=50)
    nodes, edges = flow_and_height(nodes, edges, settings)
    nodes, edges = flow_amount(nodes, edges, settings)
    edges = diameter_calc(edges, settings["diam_list"])
    nodes, edges = cleaner_and_trimmer(nodes, edges)
    nodes, edges = add_outfalls(nodes, edges, settings)


    print(nodes, edges)
    _ = plt.figure()

    height_contour_plotter(nodes, edges, 121)
    diameter_map(nodes, edges, 122)


    plt.show()


if __name__ == "__main__":
    tester()