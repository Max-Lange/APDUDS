
"""Defines the OpenStreetMap extraction and conversion functions.

This script defines the functions that facilitate the downloading and reformating
of road map data from OpenStreetMap (OSM) (using osmnx for the downloading part).
It also defines the function that splits the obtained edges into smaller equal section
as per the user defined maximum edge length.

This script requires that `osmnx`, `pandas` and `numpy` be installed within the Python
environment you are running this script in.

This file contains the following functions:

    * extractor - Downloads the wanted area from OpenStreetMap
    * fill_nan - Fills the nan values that are assigned for some elevations
    * cleaner - Cleans and standerdizes the data downloaded by the extractor
    * splitter - Splits the obtained conduits according to the given parameters
    * tester - Only used for testing purposes
"""

import osmnx as ox
import pandas as pd
import numpy as np
ox.config(use_cache=False)

def extractor(coords: list, key: str, aggregation_size=15):
    """Downloads the wanted road network from OpenStreetMap, and filters out the unwanted data

    Args:
        coords (list): noth, south, east and west coordinates of the desired bounding box
        aggregation_size (int, optional): Max distance by which to aggrigate nearby nodes.
        Defaults to 15.

    Returns:
        tuple[DataFrame, DataFrame]: The node and conduit data of the network
    """

    # Download osm data, reproject into meter-using coordinate system, consolidate nearby nodes
    cf = '["highway"~"secondary|tertiary|residential|living_street|service|pedestrian|busway|unclassified"]'
    osm_map = ox.graph_from_bbox(coords[0], coords[1], coords[2], coords[3], custom_filter=cf)
    osm_map = ox.elevation.add_node_elevations_google(osm_map, api_key=key)
    osm_map = ox.elevation.add_edge_grades(osm_map)
    

    osm_projected = ox.project_graph(osm_map)
    osm_consolidated = ox.consolidate_intersections(osm_projected,
                                                        tolerance=7,
                                                        dead_ends=True)

    # Seperate the nodes and edges, and reset multidimensional index
    osm_nodes, osm_edges = ox.graph_to_gdfs(osm_consolidated)


    nodes_reset = osm_nodes.reset_index()
    edges_reset = osm_edges.reset_index()

    #Fill NAN elevation values with average of the model. 
    # nodes_reset['elevation'].fillna(value=nodes_reset['elevation'].mean(), inplace=True)
    nodes_reset['elevation'] = nodes_reset['elevation'] - nodes_reset['elevation'].max()

    # Create new nodes and edges dataframe which only contain the desired data
    int_from = [int(edges_reset.u[i]) for i in range(len(edges_reset))]
    int_to = [int(edges_reset.v[i]) for i in range(len(edges_reset))]
    elevation = [(nodes_reset.elevation[i]) for i in range(len(nodes_reset))]

    edges = pd.DataFrame({"from":int_from,
                            "to":int_to,
                            "length":edges_reset.length})
    nodes = pd.DataFrame({"x":nodes_reset.x,
                            "y":nodes_reset.y,
                            "elevation":elevation})

    return nodes, edges

def fill_nan(nodes: pd.DataFrame, edges: pd.DataFrame):
    """Fills the NaN elevation values for the nodes

    Args:
        nodes (pd.DataFrame): The node data for a network
        edges (pd.DataFrame): The conduit data for a network

    Returns:
        tuple[DataFrame, DataFrame]: The node and conduit data with added nan values.
    """
    nodes = nodes.copy()
    edges = edges.copy()
    count, j = 0, 0
    while len(nodes[nodes["elevation"].isna()]) >= 1:
        for i, _ in nodes[nodes["elevation"].isna()].iterrows():
            length_elevation = 0
            length = 0
            for _, edge in edges[edges["from"] == i].iterrows():
                if pd.isna(nodes.at[int(edge["to"]), "elevation"]):
                    continue
                else:
                    length_elevation += edge["length"] * nodes.at[int(edge["to"]), "elevation"]
                length += edge["length"]
            for _, edge in edges[edges["to"] == i].iterrows():
                if pd.isna(nodes.at[int(edge["from"]), "elevation"]):
                    continue
                else:
                    length_elevation += edge["length"] * nodes.at[int(edge["from"]), "elevation"]
                length += edge["length"]
            try:
                nodes.at[i, "elevation"] = length_elevation / length
                count += 1
            except ZeroDivisionError:
                continue

        j += 1
        if j >= 20:
            print(f'\n Too many loops needed to interpolate elevation')
            break

    print(f"\nOf {count} node(s), the elevation was interpolated")

    return nodes, edges

def cleaner(nodes: pd.DataFrame, edges: pd.DataFrame):
    """Standerdizes and cleans the data downloaded from OpenStreetMap by the extractor

    Args:
        nodes (pd.DataFrame): The node data for a network
        edges (pd.DataFrame): The conduit data for a network

    Returns:
        tuple[DataFrame, DataFrame]: The node and conduit data with updated and cleaned values
    """

    nodes = nodes.copy()
    edges = edges.copy()

    # Reset the x and y values of the nodes to start from 0
    nodes.x = nodes.x - nodes.x.min()
    nodes.y = nodes.y - nodes.y.min()

    # And then make the center of the network the center of the axes
    nodes.x = nodes.x - (nodes.x.max() / 2)
    nodes.y = nodes.y - (nodes.y.max() / 2)

    nodes.x = nodes.x.round(decimals=2)
    nodes.y = nodes.y.round(decimals=2)

    # Duplicate edges may exist. These need to be filtered out
    combos = []
    filtered_edges = pd.DataFrame(columns=["from", "to", "length"])
    for _, line in edges.iterrows():
        if line["from"] != line["to"]:
            combo = set([line["from"], line["to"]])

            if combo not in combos:
                filtered_edges.loc[len(filtered_edges)] = [line["from"], line["to"], line["length"]]
                combos.append(combo)

    filtered_edges.length = filtered_edges.length.round(decimals=2)
    filtered_edges[["from", "to"]] = filtered_edges[["from", "to"]].astype(int)

    return nodes, filtered_edges


def splitter(nodes: pd.DataFrame, edges: pd.DataFrame, max_space: int):
    """Splits conduits which exceed a certain lenght into equally sized section,
    and connects them back up by adding nodes in the splits.

    Args:
        nodes (pd.DataFrame): The node data for a network
        edges (pd.DataFrame): The conduit data for a network
        max_space (int): The maximum allowable manhole spacing by which the conduits will be split

    Returns:
        tuple[DataFrame, DataFrame]: The node and conduit data with extra nodes and conduits added
        where conduits needed to be split.
    """

    nodes = nodes.copy()
    # Create a new dataframe to be filled with the correct edges
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

            # Determine the direction in which to advance the x and y coords and determine elevation change to new node
            x_step_size = (to_node.x - from_node.x) / (amount + 1)
            y_step_size = (to_node.y - from_node.y)  / (amount + 1)

            elevation_step_size = (to_node.elevation - from_node.elevation) / (amount + 1)

            # Special case for the first node and edge
            index_i = len(nodes)
            nodes.loc[index_i] = [from_node.x + x_step_size, from_node.y + y_step_size, from_node.elevation + elevation_step_size]
            new_edges.loc[len(new_edges)] = [line["from"], index_i, new_length]

            # Add new nodes and edges for the needed nodes in the middle
            if amount > 1:
                for i in range(2, amount+1):
                    index_i = len(nodes)
                    nodes.loc[index_i] = [from_node.x + x_step_size * i, \
                        from_node.y + y_step_size * i, from_node.elevation + elevation_step_size * i]
                    new_edges.loc[len(new_edges)] = [index_i - 1, index_i, new_length]

            # Special case for the last edge
            new_edges.loc[len(new_edges)] = [index_i, line["to"], new_length]

    # Clean up and round of the newly constructed data
    nodes.x = nodes.x.round(decimals=2)
    nodes.y = nodes.y.round(decimals=2)
    new_edges.length = new_edges.length.round(decimals=2)
    new_edges[["from", "to"]] = new_edges[["from", "to"]].astype(int)
    return nodes, new_edges


def tester():
    """Only used for testing purposes"""
    print("osm_extractor script has run")

if __name__ == "__main__":
    tester()
