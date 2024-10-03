import matplotlib.pyplot as plt
import ndlib.models.ModelConfig as mc
import ndlib.models.opinions as op
import tkinter
from ndlib.viz.mpl.OpinionEvolution import OpinionEvolution
import networkx as nx
import time
import random


#function to read the network (l[0]-> edge, l[1]-> time)
def read_net(filename):
    g = nx.Graph()
    with open(filename) as f:
        f.readline()
        for l in f:
            l = l.split(",")
            g.add_edge(l[0], l[1])
    return g

t1=time.time()
##network costruction
#read the network
g = read_net(r"D:\social_net\sna-2023-2023_batignani_fattorini_iannello\data_collection\conspiracy_2m_final.csv")
#remove the bot
g.remove_node("rConBot")
#remove the selfloops
g.remove_edges_from(nx.selfloop_edges(g))
#remove isolated nodes
g.remove_nodes_from(list(nx.isolates(g)))
#considering only the giant component
comps = list(nx.connected_components(g))
g=g.subgraph(comps[0])
#required by the library
g=nx.convert_node_labels_to_integers(g)
#mean field option
#g=nx.complete_graph(1000)

##Model simulation
#number of iterations
iter=1000
#choice of the model
model = op.AlgorithmicBiasModel(g)
#choice of the parameters
config = mc.Configuration()
config.add_model_parameter("epsilon", 0.4)
config.add_model_parameter("gamma", 0)  # No bias = Deffuant
#configuration of the parameters
model.set_initial_status(config)

# Simulation execution
iterations = model.iteration_bunch(iter)
##opinion plot
viz = OpinionEvolution(model, iterations)
plt.figure(dpi=1200)
viz.plot("deff_04.png")

print((time.time()-t1)/60.0)