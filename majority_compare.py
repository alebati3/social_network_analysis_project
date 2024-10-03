import networkx as nx
import warnings
import numpy as np
import ndlib
import matplotlib.pyplot as plt
import ndlib.models.ModelConfig as mc
import ndlib.models.opinions as op
import time

'''
script to compare the majority rule model for different choices of the q-parameter. The comparisons are shown in a diffusion trend plot with the 4 simulations
'''


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
#the label of the nodes are not necessary
g=nx.convert_node_labels_to_integers(g)
#Complete graph option
#g=nx.complete_graph(1000)

#number of iterations
it=10000
#values of parameter q to simulate with
set_of_q=np.array([10,25,50,100],dtype=int)
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
plt.title("majority rule comparisons")
plt.ylim([0,1])
plt.xlim([0,it])
plt.grid(axis='y')

##simulations with different values of q
for q in set_of_q:
    #choice of the model
    majority_model = op.MajorityRuleModel(g)
    #configuration of the model parameters
    config = mc.Configuration()
    config.add_model_parameter('q', q)
    config.add_model_parameter('fraction_infected', init_inf)
    #initialisation of the model
    majority_model.set_initial_status(config)
    # Simulation execution
    iterations = majority_model.iteration_bunch(it)
    trends= majority_model.build_trends(iterations)
    #fractions of infected nodes at each iteration are saved in a numpy array
    infected=np.array(trends[0]['trends']['node_count'][1])/nodes
    #defining the label of the plot
    lab='majority rule, q='+str(q)
    #updating the plot
    plt.plot(iter,infected, label=lab)
##showing the plot
#creation of the legend
plt.legend()
print((time.time()-t1)/60.0)
plt.show()
