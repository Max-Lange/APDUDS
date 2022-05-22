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

    nodes["area"] = voro.volumes

    return nodes, voro


def flow_and_height_original(nodes: pd.DataFrame, edges: pd.DataFrame, settings: dict):
    """Determines the direction of flow and needed installation height of the nodes based
    on the given settings (minimum slope and position of the outfall and overflow nodes)

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

    main_path = nx.dijkstra_path(graph, settings["overflow"], settings["outfall"])
    main_path = [int(x) for x in main_path]

    nodes.loc[main_path, "considered"] = True
    nodes = set_depth(nodes, edges, main_path, settings["min_slope"])


    i = 1
    while not nodes["considered"].all():
        leaf_nodes = nodes.index[nodes.connections == i].tolist()

        for node in leaf_nodes:
            if not nodes.loc[node, "considered"]:
                path = determine_path(graph, node, main_path)
                nodes.loc[path, "considered"] = True

                main_index = main_path.index(path[-1])
                path.extend(main_path[main_index+1:])

                nodes = set_depth(nodes, edges, path, settings["min_slope"])
        i += 1

    return nodes, edges


def flow_and_height_new(nodes: pd.DataFrame, edges: pd.DataFrame, settings:dict):
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
    end_point = settings["outfall"]

    nodes, edges, graph = intialize(nodes, edges, settings)
    nodes.loc[end_point, "considered"] = True

    i = 1
    while not nodes["considered"].all():
        leaf_nodes = nodes.index[nodes.connections == i].tolist()

        for node in leaf_nodes:
            if not nodes.loc[node, "considered"]:
                path = determine_path_new(graph, node, end_point)
                nodes = set_paths(nodes, path)

                nodes.loc[path, "considered"] = True
                nodes = set_depth(nodes, edges, path, settings["min_slope"])
        i += 1

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
    nodes.loc[settings["outfall"], "role"] = "outfall"
    nodes.loc[settings["overflow"], "role"] = "overflow"

    graph = nx.Graph()
    graph.add_nodes_from(list(nodes.index.values))

    for _, edge in edges.iterrows():
        graph.add_edge(edge["from"], edge["to"], weight=edge["length"])

    return nodes, edges, graph


def set_depth(nodes: pd.DataFrame, edges: pd.DataFrame, path: list, min_slope: float):
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

    edge_set = [set([edges["from"][i], edges["to"][i]]) for i in range(len(edges))]

    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i+1]

        from_depth = nodes.loc[from_node, "depth"]
        length = edges.loc[edge_set.index(set([from_node, to_node])), "length"]
        new_to_depth = from_depth + min_slope * length

        if new_to_depth > nodes.loc[to_node, "depth"]:
            nodes.loc[to_node, "depth"] = new_to_depth

    return nodes


def determine_path(graph: nx.Graph, node: pd.DataFrame, main_path: list[int]):
    """Determines the shortes path to the main path for a certain node
    using Dijkstra's shortes path algorithm

    Args:
        graph (Graph): A NetworkX Graph of the system
        node (DataFrame): The nodes of the system along with their attributes
        main_path (list[int]): All the indicies of the nodes which the path passes through
        (including start and end nodes)

    Returns:
        list[int]: The indicies of the nodes which the shortes path passes through
    """

    shortest_distance = np.inf
    best_path = []

    for option in main_path[1:]:
        distance, path = nx.single_source_dijkstra(graph, node, target=option)

        if distance < shortest_distance:
            shortest_distance = distance
            path = [int(x) for x in path]
            best_path = path

    return best_path


def determine_path_new(graph: nx.Graph, start: int, end: int):
    """Determines the shortest path for a certain point to another point using
    Dijkstra's shortes path algorithm

    Args:
        graph (Graph): A NetworkX Graph object of the system
        start (int): The index of the starting node
        end (int): The index of the end node

    Returns:
        list[int]: The indicies of the nodes which the shortes path passes through
    """

    path = nx.dijkstra_path(graph, start, end)

    return [int(x) for x in path]


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


def reset_direction(nodes: pd.DataFrame, edges: pd.DataFrame):
    """Flips the "from" and "to" columns for all conduits where necessary.

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes

    Returns:
        DataFrame: Edges data with the "from" "to" order corrected according to the depth
    """

    for i, edge in edges.iterrows():
        if nodes.loc[edge["from"], "depth"] > nodes.loc[edge["to"], "depth"]:
            edges.loc[i, "from"], edges.loc[i, "to"] = edge["to"], edge["from"]

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

    nodes["inflow"] = nodes["area"] * settings["rainfall"] * (settings["perc_hard"] / 100)

    return nodes


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

            for j, size in enumerate(diam_list):
                if size - precise_diam > 0:

                    edges.at[i, "diameter"] = diam_list[j]

    return edges



def tester():
    """Only used for testing purposes
    """
    from matplotlib import pyplot as plt
    from plotter import height_contour_plotter
    nodes = pd.read_csv("test_nodes_2.csv")
    edges = pd.read_csv("test_edges_2.csv")
    settings = {"outfall":36, "overflow":1, "min_depth":1.1, "min_slope":1/500,
                "rainfall": 70, "perc_hard": 25}
    diam_list = [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3]

    nodes, _ = voronoi_area(nodes, box_extent=50)
    nodes, edges = flow_and_height_new(nodes, edges, settings)
    nodes, edges = flow_amount(nodes, edges, settings)

    edges = diameter_calc(edges, diam_list)
    print(nodes, edges)

    _ = plt.figure()

    height_contour_plotter(nodes, edges, 111)

    plt.show()





if __name__ == "__main__":
    tester()
