# Copyright 2019 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Helper plot functions
"""

import numpy as np
import networkx as nx

import matplotlib.pyplot as plt
import matplotlib
# `Qt5Agg` works well in ipython/console
#matplotlib.use('Qt5Agg')
from matplotlib.gridspec import GridSpec

import dwave_networkx as dnx
import dimod


def plot(G, subgraphs=None, max_subs=3, subtitles=False, pos=None):
    """Plot utility"""

    if pos is None:
        pos = nx.get_node_attributes(G, 'pos')
    if not pos:
        pos = nx.spring_layout(G)

    if not subgraphs:
        axes = 1
        graph_edge_alpha = 0.2
        graph_node_alpha = 0.9

    else:
        axes = min(max_subs, len(subgraphs))
        graph_edge_alpha = 0.05
        graph_node_alpha = 0.1

        subgraph_edge_alpha = 0.4
        subgraph_node_alpha = 0.9

    fig = plt.figure(figsize=(15,5))
    gs = GridSpec(1, axes)
    
    for i in range(axes):
        ax = 'ax_' + str(i)
        ax = plt.subplot(gs[0, i])
        if subtitles:
            ax.set_title("Subproblem "+str(i+1))
           
        # edges for full graph
        nx.draw_networkx_edges(G, pos, alpha=graph_edge_alpha)

        # edges for subgraph
        if subgraphs:
            nx.draw_networkx_edges(subgraphs[i], pos, alpha=subgraph_edge_alpha)

        # nodes for full graph
        nodelist = G.nodes.keys()
        max_degree = max(dict(G.degree).values())

        # top 70% of reds cmap
        normalized_degrees = [0.3 + 0.7 * G.degree[n] / max_degree for n in nodelist]
        node_color = plt.cm.Reds([0] + normalized_degrees)[1:]
        nx.draw_networkx_nodes(G, pos, nodelist=nodelist, node_size=80, node_color=node_color, alpha=graph_node_alpha)

        # nodes for subgraph
        if subgraphs:
            sub_nodelist = subgraphs[i].nodes.keys()
            sub_node_color = [node_color[n] for n in sub_nodelist]
            nx.draw_networkx_nodes(subgraphs[i], pos, nodelist=sub_nodelist, node_size=80, node_color=sub_node_color, alpha=subgraph_node_alpha)
