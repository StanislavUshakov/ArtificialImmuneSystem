__author__ = 'Stanislav Ushakov'

from immune import ExpressionsImmuneSystem, DataFileStorageHelper
from exchanger import PeerToPeerExchanger, LocalhostNodesManager
import random
import math
import sys

#start as "python node_main.py node_num number_of_nodes"
if __name__ == '__main__':
    number = int(sys.argv[1])
    number_of_nodes = int(sys.argv[2])
    nodes_manager = LocalhostNodesManager(number, number_of_nodes)
    number_of_lymphocytes = 150
    max_height = 4

    variables, values = DataFileStorageHelper.load_from_file('test_x_y.txt')

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