__author__ = 'Stanislav Ushakov'

from immune import ExpressionsImmuneSystem, DataFileStorageHelper, ExpressionsImmuneSystemConfig
from exchanger import PeerToPeerExchanger, LocalhostNodesManager
import sys

#start as "python node_main.py node_num number_of_nodes"
if __name__ == '__main__':
    number = int(sys.argv[1])
    number_of_nodes = int(sys.argv[2])

    nodes_manager = LocalhostNodesManager(number, number_of_nodes)
    config = ExpressionsImmuneSystemConfig()
    config.number_of_lymphocytes = 150

    variables, values = DataFileStorageHelper.load_from_file('test_x_y.txt')

    exchanger = PeerToPeerExchanger(nodes_manager)

    results = []
    immuneSystem = ExpressionsImmuneSystem(exact_values=values,
            variables=variables,
            exchanger=exchanger,
            config=config)
    best = immuneSystem.solve()
    print(best)