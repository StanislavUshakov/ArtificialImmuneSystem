__author__ = 'Stanislav Ushakov'

import math
import time

from expression import Expression
from immune import ExpressionsImmuneSystem, FitnessFunction, DataFileStorageHelper
from exchanger import SimpleRandomExchanger

def update_progress(progress:int):
    """
    Shows progress bar. Progress is passed in percent.
    """
    print('\r[{0}] {1}%'.format('#' * (progress // 10), progress), end='')

if __name__ == "__main__":
    number_of_lymphocytes = 100
    max_height = 4

    #DataFileStorageHelper.save_to_file('test_x_y.txt', variables, lambda x, y: x*x + y*y*math.sin(x), 50)

    variables, values = DataFileStorageHelper.load_from_file('test_x_y.txt')

    f = FitnessFunction(values)
    exchanger = SimpleRandomExchanger(
        lambda: [Expression.generate_random(max_height=max_height, variables=variables)
                for i in range(0, number_of_lymphocytes // 2)])

    results = []
    iterations = 5
    start = time.clock()
    for i in range(0, iterations):
        immuneSystem = ExpressionsImmuneSystem(exact_values=values,
            variables=variables,
            exchanger=exchanger,
            number_of_lymphocytes=number_of_lymphocytes,
            maximal_height=max_height,
            number_of_iterations=15)
        best = immuneSystem.solve()
        results.append((f.expression_value(best), str(best)))
        update_progress(int((i+1) / iterations * 100))
    end = time.clock()
    print('\n{0} seconds'.format(end - start))
    for result in sorted(results):
        print(result, sep='\n')