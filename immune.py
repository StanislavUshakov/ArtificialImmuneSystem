__author__ = 'Stanislav Ushakov'

import math
import random
import copy

from expression import Expression

class FitnessFunction:
    """
    Used for calculating fitness function for
    given expression.
    Value is simple Euclidean norm for vector.
    """
    def __init__(self, exact_values):
        """
        Initializes function with the exact values of the needed function.
        Pass exact values in the following form:
        [({'x': 1, 'y': 1}, 0.125),
         ({'x': 2, 'y': 2}, 0.250)]
        """
        self.exact_values = exact_values

    def expression_value(self, expression:Expression):
        """
        Returns value of the fitness function for given
        expression. The less the value - the closer expression to
        the unknown function.
        """
        sum = 0
        for (variables, value) in self.exact_values:
            sum += ((expression.value_in_point(variables) - value) *
                    (expression.value_in_point(variables) - value))
        return math.sqrt(sum)


class ExpressionMutator:
    """
    This class encapsulates all logic for mutating selected lymphocytes.
    """
    def __init__(self, expression:Expression):
        """
        Initializes mutator with the given expression.
        NOTE: expression itself won't be changed. Instead of its
        changing, the new expression will be returned.
        """
        self.expression = copy.deepcopy(expression)
        self.mutations = [
            self.number_mutation,
            self.variable_mutation,
            self.unary_mutation,
            self.binary_mutation,
            self.subtree_mutation]

    def mutation(self):
        """
        Returns the mutated version of the expression.
        All mutations are of equal possibilities.
        May be change.
        """
        mutation = random.choice(self.mutations)
        mutation()
        return self.expression

    def number_mutation(self):
        """
        USed for mutate number nodes. Adds or subtracts random number from
        the value or
        """
        numbers = self._get_all_nodes_by_filter(lambda n: n.is_number())
        if not numbers: return

        selected_node = random.choice(numbers)
        if random.random() < 0.45:
            selected_node.value += random.random()
        elif random.random() < 0.9:
            selected_node.value -= random.random()
        else:
            selected_node.value = round(selected_node.value)

    def variable_mutation(self):
        """
        Changes one randomly selected variable to another, also
        randomly selected.
        """
        variables = self._get_all_nodes_by_filter(lambda n: n.is_variable())
        if not variables: return

        selected_var = random.choice(variables)
        selected_var.value = random.choice(self.expression.variables)

    def unary_mutation(self):
        """
        Changes one unary operation to another
        """
        unary_operations = self._get_all_nodes_by_filter(lambda n: n.is_unary())
        if not unary_operations: return

        selected_unary = random.choice(unary_operations)
        selected_unary.operation = random.choice(self.expression.get_unary_operations())

    def binary_mutation(self):
        """
        Changes one binary operations to another
        """
        binary_operations = self._get_all_nodes_by_filter(lambda n: n.is_binary())
        if not binary_operations: return

        selected_binary = random.choice(binary_operations)
        selected_binary.operation = random.choice(self.expression.get_binary_operations())

    def subtree_mutation(self):
        """
        Changes one randomly selected node to the randomly generated subtree.
        The height of the tree isn't changed.
        """
        nodes = self._get_all_nodes_by_filter(lambda n: n.height() > 1 and
                                                        n != self.expression.root)
        if not nodes: return

        selected_node = random.choice(nodes)
        max_height = self.expression.root.height() - selected_node.height()
        new_subtree = Expression.generate_random(max_height, self.expression.variables)
        selected_node.operation = new_subtree.root.operation
        selected_node.value = new_subtree.root.value
        selected_node.left = new_subtree.root.left
        selected_node.right = new_subtree.root.right

    def _get_all_nodes_by_filter(self, filter_func):
        """
        Used for selecting all nodes satisfying the given filter.
        """
        nodes = []

        def traverse_tree(node):
            if filter_func(node):
                nodes.append(node)
            if node.left is not None:
                traverse_tree(node.left)
            if node.right is not None:
                traverse_tree(node.right)
        traverse_tree(self.expression.root)

        return nodes


class ExpressionsImmuneSystem:
    """
    Class represents entire immune system.
    Now - this is simply algorithm, that works for a number of steps.
    On each step the best lymphocytes are selected for the mutation.
    """
    maximal_height = 4
    number_of_lymphocytes = 100
    number_of_iterations = 30

    def __init__(self, exact_values, variables, **configuration):
        """
        Initializes the immune system with the provided parameters (or
        default parameters if not provided).
        lymphocytes - list that stores current value of the whole system.
        """
        self.exact_values = exact_values
        self.variables = variables
        self.fitness_function = FitnessFunction(exact_values)

        #config
        self.number_of_lymphocytes = (
            configuration['number_of_lymphocytes']
            if 'number_of_lymphocytes' in configuration
            else ExpressionsImmuneSystem.number_of_lymphocytes)
        self.number_of_iterations = (
            configuration['number_of_iterations']
            if 'number_of_iterations' in configuration
            else ExpressionsImmuneSystem.number_of_iterations)

        self.lymphocytes = []
        for i in range(0, self.number_of_lymphocytes):
            self.lymphocytes.append(Expression.generate_random(
                                        ExpressionsImmuneSystem.maximal_height,
                                        variables))

        random.seed()

    def solve(self, accuracy=0.001):
        """
        After defined number of steps returns the best lymphocyte as
        an answer.
        """
        for i in range(0, self.number_of_lymphocytes):
            self.step()
            best = self.best()
            if self.fitness_function.expression_value(best) <= accuracy:
                best.simplify()
                return best

        best = self.best()
        best.simplify()
        return best

    def step(self):
        """
        Represents the step of the solution finding.
        The half of the lymphocytes are mutated. The new system
        consists of this half and their mutated 'children'.
        """
        sorted_lymphocytes = self._get_sorted_lymphocytes_index_and_value()
        best = []
        for (i, e) in sorted_lymphocytes[:self.number_of_lymphocytes // 2]:
            best.append(self.lymphocytes[i])
        mutated = [ExpressionMutator(e).mutation() for e in best]
        self.lymphocytes = best + mutated

    def best(self):
        """
        Returns the best lymphocyte in the system.
        """
        return self.lymphocytes[self._get_sorted_lymphocytes_index_and_value()[0][0]]

    def _get_sorted_lymphocytes_index_and_value(self):
        """
        Returns list of lymphocytes and their numbers in the original system
        in sorted order.
        """
        fitness_values = []
        for (i, e) in enumerate(self.lymphocytes):
            fitness_values.append((i, self.fitness_function.expression_value(e)))
        return sorted(fitness_values, key=lambda item: item[1])
