import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from osm_extractor import extractor, cleaner, splitter
from scipy.interpolate import Rbf




nodes, edges = extractor([47.348854, filtered_nodes, filtered_edges = cleaner(nodes, edges)
split_nodes, split_edges = splitter(filtered_nodes, filtered_edges, 200)

mq = Rbf(split_nodes.x, split_nodes.y, split_nodes.elevation, epsilon=5)
xg, yg = np.meshgrid(np.linspace(split_nodes.x.min() * 2, split_nodes.x.max() * 2, 400), np.linspace(split_nodes.y.min() * 2, split_nodes.y.max() * 2, 400))
zg = mq(xg, yg)
plt.figure(figsize=(6, 6))
cs = plt.contour(xg, yg, zg, np.arange(0, split_nodes.elevation.max(), 2))
plt.clabel(cs, fmt='%1.0f')
plt.plot(split_nodes.x, split_nodes.y, 'o')
# for i in range(len(xm)):
#     plt.text(xm[i], ym[i] + 0.5, str(zm[i]), ha='center')
plt.axis('scaled')
plt.show()
print("last")