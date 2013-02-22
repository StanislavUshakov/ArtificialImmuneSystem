__author__ = 'Stanislav Ushakov'

import random
import math
import time

from immune import ExpressionsImmuneSystem, FitnessFunction

def update_progress(progress:int):
    """
    Shows progress bar. Progress is passed in percent.
    """
    print('\r[{0}] {1}%'.format('#' * (progress // 10), progress), end='')

if __name__ == "__main__":
    values = []
    for i in range(0,25):
        x = (0.5 - random.random()) * 50
        y = (0.5 - random.random()) * 50
        values.append(({'x': x}, x*x + x * math.sin(x) + x + 1 ))

    f = FitnessFunction(values)

    results = []
    iterations = 10
    start = time.clock()
    for i in range(0, iterations):
        immuneSystem = ExpressionsImmuneSystem(exact_values=values,
            variables=['x'],
            number_of_lymphocytes=200,
            number_of_iterations=2)
        best = immuneSystem.solve()
        results.append((f.expression_value(best), str(best)))
        update_progress(int((i+1) / iterations * 100))
    end = time.clock()
    print('\n{0} seconds'.format(end - start))
    for result in sorted(results):
        print(result, sep='\n')
