import osmnx as ox
import pandas as pd
import numpy as np
# Download osm data, reproject into meter-using coordinate system, consolidate nearby nodes
cf = '["highway"~"tertiary|secondary|residential"]'

# osm_map = ox.graph_from_bbox(51.85630, 51.85466, 5.00908, 5.00647, network_type='drive')
osm_map = ox.graph_from_bbox(51.92094, 51.91054, 4.33346, 4.31215, custom_filter=cf)
ox.plot.plot_graph(osm_map) 
    #Cf tertiary road, residential road, secondary road, service road, living street, pedestrian way, 
osm_projected = ox.project_graph(osm_map)
aggregation_size = 15
osm_consolidated = ox.consolidate_intersections(osm_projected,
                                                    tolerance=aggregation_size,
                                                    dead_ends=True)
ox.plot.plot_graph(osm_map) 

    # Seperate the nodes and edges, and reset multidimensional index
osm_nodes, osm_edges = ox.graph_to_gdfs(osm_consolidated)
nodes_reset = osm_nodes.reset_index()
edges_reset = osm_edges.reset_index()
print(nodes_reset)

    # Create new nodes and edges dataframe which only contain the desired data
int_from = [int(edges_reset.u[i]) for i in range(len(edges_reset))]
int_to = [int(edges_reset.v[i]) for i in range(len(edges_reset))]
edges = pd.DataFrame({"from":int_from,
                        "to":int_to,
                        "length":edges_reset.length})
nodes = pd.DataFrame({"x":nodes_reset.x,
                        "y":nodes_reset.y,})


