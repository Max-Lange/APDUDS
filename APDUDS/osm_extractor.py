"""OpenStreepMap data extractor and reformator

This script defines the functions that facilitate the downloading and reformating
of road map data from OpenStreetMap (OSM) (using osmnx for the downloading part).
It also defines the function that splits the obtained edges into smaller equal section
as per the user defined maximum edge length.

This script requires that `osmnx, pandas and numpy` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * extractor - Downloads the wanted area from OSM and reformats the obtained data
    * splitter - Splits the obtained edges to be smaller than the specified maximum length
    * main - Only used for testing purposes
"""

import osmnx as ox
import pandas as pd
import numpy as np
ox.config(use_cache=False)


def extractor(coords: list, aggregation_size=10):
    """Downloads the road network for the selected bounding box from OpenStreetMap using osmnx

    Args:
        coords (list): nort, south, east and west coordinates of the wanted bountding box
        aggregation_size (int, optional): Max distance for which nearby points are
        consolidated. Defaults to 10.

    Returns:
        tuple: Two Dataframes containing the node and edge data respectively
    """

    # Download osm data, reproject into meter-using coordinate system, consolidate nearby nodes
    osm_map = ox.graph_from_bbox(coords[0], coords[1], coords[2], coords[3], network_type="drive")

    osm_projected = ox.project_graph(osm_map)
    osm_consolidated = ox.consolidate_intersections(osm_projected,
                                                    tolerance=aggregation_size,
                                                    dead_ends=True)

    # Seperate the nodes and edges, and reset multidimensional index
    osm_nodes, osm_edges = ox.graph_to_gdfs(osm_consolidated)
    nodes_reset = osm_nodes.reset_index()
    edges_reset = osm_edges.reset_index()

    # Create new nodes and edges dataframe which only contain the wanted data
    int_from = [int(edges_reset.u[i]) for i in range(len(edges_reset))]
    int_to = [int(edges_reset.v[i]) for i in range(len(edges_reset))]
    edges = pd.DataFrame({"from":int_from,
                          "to":int_to,
                          "length":edges_reset.length})
    nodes = pd.DataFrame({"x":nodes_reset.x,
                          "y":nodes_reset.y,})

    return nodes, edges


def cleaner(nodes: pd.DataFrame, edges: pd.DataFrame):
    """_summary_

    Args:
        nodes (pd.DataFrame): positional (x, y) data of the nodes
        edges (pd.DataFrame): from, to and length data of the edges (lines) of the network

    Returns:
        tuple[Dataframe, Dataframe]: Dataframes for the (filtered) nodes and edges
    """

    nodes = nodes.copy()
    edges = edges.copy()

    # Reset the x and y values of the nodes to start from 0
    nodes.x = nodes.x - nodes.x.min()
    nodes.y = nodes.y - nodes.y.min()

    # And then make the center of the network the center of the axes
    nodes.x = nodes.x - (nodes.x.max() / 2)
    nodes.y = nodes.y - (nodes.y.max() / 2)

    # Duplicate edges may exist. These need to be filtered out
    combos = []
    filtered_edges = pd.DataFrame(columns=["from", "to", "length"])
    for _, line in edges.iterrows():
        if line["from"] != line["to"]:
            combo = set([line["from"], line["to"]])

            if combo not in combos:
                filtered_edges.loc[len(filtered_edges)] = [line["from"], line["to"], line["length"]]
                combos.append(combo)

    return nodes, filtered_edges



def splitter(nodes: pd.DataFrame, edges: pd.DataFrame, max_space: int):
    """_summary_

    Args:
        nodes (DataFrame): positional (x, y) data of the nodes
        edges (DataFrame): from, to and length data of the edges (lines) of the network
        max_space (int): maximum space between two nodes (max length of an edge)

    Returns:
        tuple[Dataframe, Dataframe]: Dataframes for the nodes and (split) edges
    """

    nodes = nodes.copy()
    new_edges = pd.DataFrame(columns=["from", "to", "length"])
    for _, line in edges.iterrows():
        # If the line is below the max_length, just add it to the new dataframe
        if line.length <= max_space:
            new_edges.loc[len(new_edges)] = [line["from"], line["to"], line["length"]]

        # Otherwise it needs to be split
        else:
            from_node = nodes.iloc[int(line["from"])]
            to_node = nodes.iloc[int(line["to"])]

            # Amount of splits, new lenght of resulting pipe sections, and x,y stepsize
            amount = int(np.ceil(line["length"] / max_space) - 1)
            new_length = line["length"] / (amount + 1)

            # Determine the direction in which to advance the x and y coords
            x_step_size = (to_node.x - from_node.x) / (amount + 1)
            y_step_size = (to_node.y - from_node.y)  / (amount + 1)

            # Special case for the first node and edge
            index_i = len(nodes)
            nodes.loc[index_i] = [from_node.x + x_step_size, from_node.y + y_step_size]
            new_edges.loc[len(new_edges)] = [line["from"], index_i, new_length]

            # Add new nodes and edges for the needed nodes in the middle
            if amount > 1:
                for i in range(2, amount+1):
                    index_i = len(nodes)
                    nodes.loc[index_i] = [from_node.x + x_step_size * i, \
                        from_node.y + y_step_size * i]
                    new_edges.loc[len(new_edges)] = [index_i - 1, index_i, new_length]

            # Special case for the last edge
            new_edges.loc[len(new_edges)] = [index_i, line["to"], new_length]

    return nodes, new_edges


def main():
    """Only used for testing purposes"""
    nodes, edges = extractor([51.9293, 51.9207, 4.8378, 4.8176])
    nodes, edges = cleaner(nodes, edges)
    nodes, edges = splitter(nodes, edges, 150)

    ruined_edges = edges.copy()
    edges_melted = ruined_edges[["from", "to"]].melt(var_name='columns', value_name='index')
    edges_melted["index"] = edges_melted["index"].astype(int)
    nodes["connections"] = edges_melted["index"].value_counts().sort_index()

    edges[["from", "to"]] = edges[["from", "to"]].astype(int)


    nodes.to_csv("test_nodes_2.csv")
    edges.to_csv("test_edges_2.csv")

if __name__ == "__main__":
    main()
