__author__ = 'Stanislav Ushakov'

import sys
import time
from subprocess import Popen

#start as local_server.py number_of_nodes
if __name__ == '__main__':
    nodes = int(sys.argv[1])

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0

    processes = []
    for i in range(0, nodes):
        print('Starting {0}...'.format(i))
        processes.append(Popen('python node_main.py ' + str(i + 1) + ' ' + str(nodes)))
    while True:
        for p in processes:
            if done(p):
                if success(p):
                    processes.remove(p)
                else:
                    print('Error')

        if not processes:
            break
        else:
            time.sleep(0.05)
