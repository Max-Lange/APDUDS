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
    edges = pd.DataFrame({"from":int_from, "to":int_to, "length":edges_reset.length})
    nodes = pd.DataFrame({"x":nodes_reset.x, "y":nodes_reset.y})

    # Two edges may exist between the same two nodes, filter these out
    combos = []
    filtered_edges = pd.DataFrame(columns=["from", "to", "length"])
    for _, line in edges.iterrows():
        combo = set([line["from"], line["to"]])

        if combo not in combos:
            filtered_edges.loc[len(filtered_edges)] = [line["from"], line["to"], line["length"]]
            combos.append(combo)

    # Reset the x and y values of the nodes to start from 0
    nodes.x = nodes.x - nodes.x.min()
    nodes.y = nodes.y - nodes.y.min()

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
            amount = int(line["length"] // max_space)
            new_length = line["length"] / (amount + 1)
            step = np.sqrt((to_node.y - from_node.y) ** 2 + \
                (to_node.x - from_node.x) ** 2) / (amount)

            # Determine the direction in which to advance the x and y coords
            if to_node.x == from_node.x:
                slope = np.inf

            else:
                slope = (to_node.y - from_node.y) / (to_node.x - from_node.x)

            relation = np.sqrt(slope ** 2 + 1)

            if to_node.x - from_node.x < 0:
                relation *= -1

            new_x = from_node.x + (step / relation)

            if slope == np.inf:
                new_y = from_node.y + step

            else:
                new_y = from_node.y + ((slope * step) / relation)

            # Special case for the first node and edge
            index_i = len(nodes)
            nodes.loc[index_i] = [new_x, new_y]
            new_edges.loc[len(new_edges)] = [line["from"], index_i, new_length]

            # Add new nodes and edges for the needed nodes in the middle
            for i in range(2, amount):
                new_x = from_node.x + (step / relation) * i

                if slope == np.inf:
                    new_y = from_node.y + step * i

                else:
                    new_y = from_node.y + ((slope * step) / relation) * i

                index_i = len(nodes)
                nodes.loc[index_i] = [new_x, new_y]
                new_edges.loc[len(new_edges)] = [index_i - 1, index_i, new_length]

            # Special case for the last edge
            new_edges.loc[len(new_edges)] = [index_i, line["to"], new_length]

    return nodes, new_edges


def main():
    """Only used for testing purposes"""
    # nodes, edges = extractor([51.9293, 51.9207, 4.8378, 4.8176])


if __name__ == "__main__":
    main()
