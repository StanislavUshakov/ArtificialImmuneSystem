__author__ = 'Stanislav Ushakov'

import unittest
import pickle

from expression import Expression, NotSupportedOperationError, Operations, Node
from immune import FitnessFunction, ExpressionMutator, ExpressionsImmuneSystem
from exchanger import SimpleRandomExchanger, LocalhostNodesManager

class OperationTest(unittest.TestCase):
    def test_pickle_number(self):
        operation = Operations.NUMBER
        returned_operation = pickle.loads(pickle.dumps(operation))
        self._test_for_equality(operation, returned_operation)

    def test_pickle_variable(self):
        operation = Operations.IDENTITY
        returned_operation = pickle.loads(pickle.dumps(operation))
        self._test_for_equality(operation, returned_operation)

    def test_pickle_unary(self):
        operation = Operations.SIN
        returned_operation = pickle.loads(pickle.dumps(operation))
        self._test_for_equality(operation, returned_operation)

    def test_pickle_binary(self):
        operation = Operations.MINUS
        returned_operation = pickle.loads(pickle.dumps(operation))
        self._test_for_equality(operation, returned_operation)

    def _test_for_equality(self, op1, op2):
        self.assertEqual(op1._operation_type, op2._operation_type)
        self.assertEqual(op1.action, op2.action)
        if hasattr(op1, 'string_representation'):
            self.assertEqual(op1.string_representation, op2.string_representation)

class ExpressionNodeTest(unittest.TestCase):
    def test_allowed_operation(self):
        node = Node(Operations.MINUS)
        self.assertEquals(node.operation, Operations.MINUS)

    def test_not_allowed_operation(self):
        self.assertRaises(NotSupportedOperationError,
                          Node,
                          'NOT_SUPPORTED_OPERATION')

    def test_value_in_point(self):
        node = Node(Operations.MINUS,
                left=Node(Operations.IDENTITY, value='x'),
                right=Node(Operations.IDENTITY, value='y'))
        result = node.value_in_point({'x': 2, 'y': 1})
        self.assertEqual(result, 1.0)

    def test_simplify_two_numbers(self):
        node = Node(Operations.MINUS,
            left=Node(Operations.NUMBER, value=2),
            right=Node(Operations.NUMBER, value=2))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.left, None)
        self.assertEqual(node.right, None)
        self.assertEqual(node.value, 0.0)

    def test_simplify_unary_and_number(self):
        node = Node(Operations.SIN,
            left=Node(Operations.NUMBER, value=0))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.left, None)
        self.assertEqual(node.value, 0.0)

    def test_simplify_identical_variables_division(self):
        node = Node(Operations.DIVISION,
            left=Node(Operations.IDENTITY, value='x'),
            right=Node(Operations.IDENTITY, value='x'))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.left, None)
        self.assertEqual(node.right, None)
        self.assertEqual(node.value, 1.0)

    def test_simplify_multiply_by_one_right(self):
        node = Node(Operations.MULTIPLICATION,
            left=Node(Operations.IDENTITY, value='x'),
            right=Node(Operations.NUMBER, value=1))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.operation, Operations.IDENTITY)
        self.assertEqual(node.value, 'x')

    def test_simplify_multiply_by_one_left(self):
        node = Node(Operations.MULTIPLICATION,
            left=Node(Operations.NUMBER, value=1),
            right=Node(Operations.IDENTITY, value='x'))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.operation, Operations.IDENTITY)
        self.assertEqual(node.value, 'x')

    def test_pickle_node(self):
        node = Node(Operations.PLUS,
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='x'),
                right=Node(Operations.NUMBER, value=4)),
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='y'),
                right=Node(Operations.NUMBER, value=2)))
        returned_node = pickle.loads(pickle.dumps(node))
        self.assertEqual(node.operation._operation_type, returned_node.operation._operation_type)
        self.assertEqual(node.operation.action, returned_node.operation.action)
        self.assertEqual(node.value, returned_node.value)
        self.assertEqual(node.left.operation._operation_type, returned_node.left.operation._operation_type)
        self.assertEqual(node.left.operation.action, returned_node.left.operation.action)
        self.assertEqual(node.left.value, returned_node.left.value)
        self.assertEqual(node.right.operation._operation_type, returned_node.right.operation._operation_type)
        self.assertEqual(node.right.operation.action, returned_node.right.operation.action)
        self.assertEqual(node.right.value, returned_node.right.value)

class ExpressionTest(unittest.TestCase):
    def test_pickle_expression(self):
        node = Node(Operations.PLUS,
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='x'),
                right=Node(Operations.NUMBER, value=4)),
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='y'),
                right=Node(Operations.NUMBER, value=2)))
        e = Expression(root=node, variables=['x', 'y'])
        returned_expression = pickle.loads(pickle.dumps(e))
        self.assertEqual(e.variables, returned_expression.variables)
        self.assertEqual(e.root.operation._operation_type, returned_expression.root.operation._operation_type)
        self.assertEqual(e.root.operation.action, returned_expression.root.operation.action)
        self.assertEqual(e.root.value, returned_expression.root.value)
        self.assertEqual(e.root.left.operation._operation_type, returned_expression.root.left.operation._operation_type)
        self.assertEqual(e.root.left.operation.action, returned_expression.root.left.operation.action)
        self.assertEqual(e.root.left.value, returned_expression.root.left.value)
        self.assertEqual(e.root.right.operation._operation_type, returned_expression.root.right.operation._operation_type)
        self.assertEqual(e.root.right.operation.action, returned_expression.root.right.operation.action)
        self.assertEqual(e.root.right.value, returned_expression.root.right.value)

class FitnessFunctionTest(unittest.TestCase):
    def setUp(self):
        values = [({'x': i , 'y': j}, 4 * i + 2 * j)
                  for i in range(0, 10)
                  for j in range(0, 10)]
        self.f = FitnessFunction(values)

    def test_exact_value(self):
        answer = Node(Operations.PLUS,
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='x'),
                right=Node(Operations.NUMBER, value=4)),
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='y'),
                right=Node(Operations.NUMBER, value=2)))
        e = Expression(root=answer, variables=['x', 'y'])
        self.assertEqual(self.f.expression_value(e), 0.0)

    def test_wrong_value(self):
        wrong = Node(Operations.MINUS,
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='x'),
                right=Node(Operations.NUMBER, value=4)),
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='y'),
                right=Node(Operations.NUMBER, value=2)))
        e = Expression(root=wrong, variables=['x', 'y'])
        self.assertGreater(self.f.expression_value(e), 0.0)


class ExpressionMutatorTest(unittest.TestCase):
    def setUp(self):
        root = Node(Operations.PLUS,
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='x'),
                right=Node(Operations.NUMBER, value=4)),
            Node(Operations.MULTIPLICATION,
                left=Node(Operations.IDENTITY, value='y'),
                right=Node(Operations.NUMBER, value=2)))
        self.f = Expression(root=root, variables=['x', 'y'])

    def test_number_mutation(self):
        mutator = ExpressionMutator(expression=self.f)
        mutator.number_mutation()
        point = {'x': 1, 'y': 2}
        original_value = self.f.value_in_point(point)
        mutated_value = mutator.expression.value_in_point(point)
        self.assertNotEqual(original_value, mutated_value)

class LocalhostNodesManagerTest(unittest.TestCase):
    def test_self_address(self):
        manager = LocalhostNodesManager(1, 2)
        self.assertEqual(manager.get_self_address()[0], 'localhost')
        self.assertGreaterEqual(manager.get_self_address()[1], 1024)

    def test_nodes_address(self):
        manager = LocalhostNodesManager(1, 2)
        self.assertEqual(manager.get_next_node_address()[0], 'localhost')
        self.assertNotEqual(manager.get_self_address()[1], manager.get_next_node_address()[1])

class ExpressionsImmuneSystemTest(unittest.TestCase):
    def test_solve_is_not_crashing(self):
        values = []
        for i in range(0,5):
            x = i
            values.append(({'x': x}, x * x ))

        f = FitnessFunction(values)
        exchanger = SimpleRandomExchanger(
            lambda: [Expression.generate_random(max_height=2, variables=['x'])
                     for i in range(0, 5)])

        immuneSystem = ExpressionsImmuneSystem(exact_values=values,
                variables=['x'],
                number_of_lymphocytes=10,
                number_of_iterations=5,
                exchanger=exchanger)
        best = immuneSystem.solve()
        self.assertGreaterEqual(f.expression_value(best), 0)