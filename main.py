__author__ = 'Stanislav Ushakov'

import random
import math
import time

from expression import Expression
from immune import ExpressionsImmuneSystem, FitnessFunction
from exchanger import SimpleRandomExchanger

def update_progress(progress:int):
    """
    Shows progress bar. Progress is passed in percent.
    """
    print('\r[{0}] {1}%'.format('#' * (progress // 10), progress), end='')

if __name__ == "__main__":
    values = []
    variables = ['x']
    number_of_lymphocytes = 150
    max_height = 4

    for i in range(0,25):
        x = (0.5 - random.random()) * 50
        y = (0.5 - random.random()) * 50
        values.append(({'x': x}, x*x + x*math.sin(x) ))

    f = FitnessFunction(values)
    exchanger = SimpleRandomExchanger(
        lambda: [Expression.generate_random(max_height=max_height, variables=variables)
                for i in range(0, number_of_lymphocytes // 2)])

    results = []
    iterations = 10
    start = time.clock()
    for i in range(0, iterations):
        immuneSystem = ExpressionsImmuneSystem(exact_values=values,
            variables=variables,
            exchanger=exchanger,
            number_of_lymphocytes=number_of_lymphocytes,
            maximal_height=max_height,
            number_of_iterations=150)
        best = immuneSystem.solve()
        results.append((f.expression_value(best), str(best)))
        update_progress(int((i+1) / iterations * 100))
    end = time.clock()
    print('\n{0} seconds'.format(end - start))
    for result in sorted(results):
        print(result, sep='\n')