__author__ = 'Stanislav Ushakov'

from immune import ExpressionsImmuneSystem
from exchanger import PeerToPeerExchanger, LocalhostNodesManager
import random
import math
import sys

#start as "python node_main.py node_num number_of_nodes"
if __name__ == '__main__':
    number = int(sys.argv[1])
    number_of_nodes = int(sys.argv[2])
    nodes_manager = LocalhostNodesManager(number, number_of_nodes)
    values = []
    variables = ['x']
    number_of_lymphocytes = 150
    max_height = 4

    for i in range(0,50):
        x = (0.5 - random.random()) * 50
        y = (0.5 - random.random()) * 50
        values.append(({'x': x}, x*x + x*math.sin(x) ))

    exchanger = PeerToPeerExchanger(nodes_manager)

    results = []
    immuneSystem = ExpressionsImmuneSystem(exact_values=values,
            variables=variables,
            exchanger=exchanger,
            number_of_lymphocytes=number_of_lymphocytes,
            maximal_height=max_height,
            number_of_iterations=150)
    best = immuneSystem.solve()
    print(best)