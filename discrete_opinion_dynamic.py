import networkx as nx
import warnings
import numpy as np
import ndlib
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
import ndlib.models.ModelConfig as mc
import ndlib.models.opinions as op
from ndlib.viz.mpl.TrendComparison import DiffusionTrendComparison
import time

'''
The script simulates all models of discrete opinion dynamics. For each model, a diffusion trend plot is saved as a png image.

Morever, a diffusion trend comparison is saved, putting all the models together

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
#labels are useless
g=nx.convert_node_labels_to_integers(g)
#Complete graph for the mean field setting
#g=nx.complete_graph(1000)
#number of iterations
it=10000
#percentage of infected nodes
init_inf=0.60
#q parameter for majority rule model
q_maj=10
#parameter for qvoter model model
q_voter=5


##voter model
#selection of the model
voter_model = op.VoterModel(g)
#parameter and initial condition configuration
config = mc.Configuration()
config.add_model_parameter('fraction_infected', init_inf)
voter_model.set_initial_status(config)
# Simulation execution
iterations = voter_model.iteration_bunch(it)
trends_voter = voter_model.build_trends(iterations)

viz = DiffusionTrend(voter_model, trends_voter)
viz.plot('provacsas.png')
print('voter done')

t2=time.time()
print((t2-t1)/60.0)

##Majority model
#selection of the model
majority_model = op.MajorityRuleModel(g)
#parameter and initial condition configuration
config = mc.Configuration()
config.add_model_parameter('q', q_maj)
config.add_model_parameter('fraction_infected', init_inf)
majority_model.set_initial_status(config)
# Simulation execution
iterations = majority_model.iteration_bunch(it)
trends_maj = majority_model.build_trends(iterations)
#plot of the diffusion trend
viz = DiffusionTrend(majority_model, trends_maj)
viz.plot('Majority060_100.png')
print('majority done')

print((time.time()-t1)/60.0)

##Sznajd Model
#selection of the model
sznajd_model = op.SznajdModel(g)
#parameter and initial condition configuration
config = mc.Configuration()
config.add_model_parameter('fraction_infected', init_inf)
sznajd_model.set_initial_status(config)
# Simulation execution
iterations = sznajd_model.iteration_bunch(it)
trends_sznajd = sznajd_model.build_trends(iterations)
#plot of the diffusion trend
viz = DiffusionTrend(sznajd_model, trends_sznajd)
viz.plot('Sznajd060.png')

print ('Sznajd done')
print((time.time()-t1)/60.0)

##Q-voter
#selection of the model
q_voter_model = op.QVoterModel(g)
#parameter and initial condition configuration
config = mc.Configuration()
config.add_model_parameter("q", q_voter)
config.add_model_parameter('fraction_infected', init_inf)
q_voter_model.set_initial_status(config)
# Simulation execution
iterations = q_voter_model.iteration_bunch(it)
trends_q = q_voter_model.build_trends(iterations)
#plot of the diffusion trend
viz = DiffusionTrend(q_voter_model, trends_q)
viz.plot("qvoter060_100.png")

print('Q-voter done')
print((time.time()-t1)/60.0)


##models comparison
#plot of the comparisons between the 4 models
viz =DiffusionTrendComparison([voter_model,majority_model,sznajd_model,q_voter_model], [trends_voter, trends_maj, trends_sznajd,trends_q])
viz.plot("trend_comparison_060_comp.png")

print((time.time()-t1)/60.0)
