import networkx as nx
import warnings
import pandas as pd
import numpy as np
import ndlib

import matplotlib.pyplot as plt
import ndlib.models.ModelConfig as mc
import ndlib.models.opinions as op
import tkinter
import random
import time


'''
script to compare the Q-voter model for different choices of the q-parameter. The comparisons are shown in a diffusion trend plot with the 4 simulations
'''





##function to sample a connected number of nodes of the initial network, by the use of a random walk process

def random_walk_sampling_simple(complete_graph, nodes_to_sample):
        #not keepinh the nodes label
        complete_graph = nx.convert_node_labels_to_integers(complete_graph, 0, 'default', True)
        # giving unique id to every node same as built-in function id
        for n, data in complete_graph.nodes(data=True):
            complete_graph.nodes[n]['id'] = n
        nr_nodes = len(complete_graph.nodes())
        #number of nodes to sample
        upper_bound_nr_nodes_to_sample = nodes_to_sample
        #randomly selecting the first node
        index_of_first_random_node = random.randint(0, nr_nodes - 1)
        #initailisation of the sample graph
        sampled_graph = nx.Graph()
        #adding the first selected node
        sampled_graph.add_node(complete_graph.nodes[index_of_first_random_node]['id'])

        iteration = 1
        edges_before_t_iter = 0
        #will be updated in the random walk process
        curr_node = index_of_first_random_node
        while sampled_graph.number_of_nodes() != upper_bound_nr_nodes_to_sample:
            #neighbours of the selected node
            edges = [n for n in complete_graph.neighbors(curr_node)]
            #randomly selecting one of the neighbours of the node
            index_of_edge = random.randint(0, len(edges) - 1)
            chosen_node = edges[index_of_edge]
            #adding the new node and linking it with the previous one
            sampled_graph.add_node(chosen_node)
            sampled_graph.add_edge(curr_node, chosen_node)
            #updating the selected node to the new one
            curr_node = chosen_node
            iteration = iteration + 1
        #to keep thw original link, i create a subgraph of the original graph with the sampled nodes
        final_graph=complete_graph.subgraph(list(sampled_graph.nodes()))
        return final_graph



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
#selecting a sample of the original network; convergence is too slow with the original one, beacuse of the large size
g = random_walk_sampling_simple(g, 5000)
#labels are useless
g=nx.convert_node_labels_to_integers(g)
#Complete graph option
#g=nx.complete_graph(1000)
#number of iterations
it=50
#values of parameter q to simulate with
set_of_q=np.array([2,5,10,50],dtype=int)
#array of each iteration: will be used in the plot
iter=np.arange(0,it,1)
#initial fraction of infected nodes
init_inf=0.60
#saving the number of nodes of the network
nodes=g.number_of_nodes()
##figure settings
plt.figure(1)
plt.xlabel('Iterations')
plt.ylabel('% nodes')
plt.title("Q-voter model comparisons")
plt.ylim([0,1.03])
plt.xlim([0,it])
plt.grid(axis='y')

##simulations with different values of q
for q in set_of_q:
    #choice of the model
    model = op.QVoterModel(g)
    #configuration of the model parameters
    config = mc.Configuration()
    config.add_model_parameter("q", q)
    config.add_model_parameter('fraction_infected', init_inf)
    #initialisation of the model
    model.set_initial_status(config)
    # Simulation execution
    iterations = model.iteration_bunch(it)
    trends = model.build_trends(iterations)

    #fractions of infected nodes at each iteration are saved in a numpy array
    infected=np.array(trends[0]['trends']['node_count'][1])/nodes
    #defining the label of the plot
    lab='majority rule, q='+str(q)
    #updating the plot
    plt.plot(np.arange(0,it,1),infected, label=lab)

##showing the plot
#creation of the legend
plt.legend()
print((time.time()-t1)/60.0)
plt.show()


