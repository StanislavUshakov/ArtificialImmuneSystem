__author__ = 'Stanislav Ushakov'

import unittest

from expression import Expression, NotSupportedOperationError
from immune import FitnessFunction, ExpressionMutator, ExpressionsImmuneSystem

class ExpressionNodeTest(unittest.TestCase):
    def test_allowed_operation(self):
        node = Expression.Node('MINUS')
        self.assertEquals(node.operation, 'MINUS')

    def test_not_allowed_operation(self):
        self.assertRaises(NotSupportedOperationError,
                          Expression.Node,
                          'NOT_SUPPORTED_OPERATION')

    def test_value_in_point(self):
        node = Expression.Node('MINUS',
                left=Expression.Node('IDENTITY', value='x'),
                right=Expression.Node('IDENTITY', value='y'))
        result = node.value_in_point({'x': 2, 'y': 1})
        self.assertEqual(result, 1.0)

    def test_simplify_two_numbers(self):
        node = Expression.Node('MINUS',
            left=Expression.Node('NUMBER', value=2),
            right=Expression.Node('NUMBER', value=2))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.left, None)
        self.assertEqual(node.right, None)
        self.assertEqual(node.value, 0.0)

    def test_simplify_unary_and_number(self):
        node = Expression.Node('SIN',
            left=Expression.Node('NUMBER', value=0))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.left, None)
        self.assertEqual(node.value, 0.0)

    def test_simplify_identical_variables_division(self):
        node = Expression.Node('DIVISION',
            left=Expression.Node('IDENTITY', value='x'),
            right=Expression.Node('IDENTITY', value='x'))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.left, None)
        self.assertEqual(node.right, None)
        self.assertEqual(node.value, 1.0)

    def test_simplify_multiply_by_one_right(self):
        node = Expression.Node('MULTIPLICATION',
            left=Expression.Node('IDENTITY', value='x'),
            right=Expression.Node('NUMBER', value=1))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.operation, 'IDENTITY')
        self.assertEqual(node.value, 'x')

    def test_simplify_multiply_by_one_left(self):
        node = Expression.Node('MULTIPLICATION',
            left=Expression.Node('NUMBER', value=1),
            right=Expression.Node('IDENTITY', value='x'))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.operation, 'IDENTITY')
        self.assertEqual(node.value, 'x')

class FitnessFunctionTest(unittest.TestCase):
    def setUp(self):
        values = [({'x': i , 'y': j}, 4 * i + 2 * j)
                  for i in range(0, 10)
                  for j in range(0, 10)]
        self.f = FitnessFunction(values)

    def test_exact_value(self):
        answer = Expression.Node('PLUS',
            Expression.Node('MULTIPLICATION',
                left=Expression.Node('IDENTITY', value='x'),
                right=Expression.Node('NUMBER', value=4)),
            Expression.Node('MULTIPLICATION',
                left=Expression.Node('IDENTITY', value='y'),
                right=Expression.Node('NUMBER', value=2)))
        e = Expression(root=answer, variables=['x', 'y'])
        self.assertEqual(self.f.expression_value(e), 0.0)

    def test_wrong_value(self):
        wrong = Expression.Node('MINUS',
            Expression.Node('MULTIPLICATION',
                left=Expression.Node('IDENTITY', value='x'),
                right=Expression.Node('NUMBER', value=4)),
            Expression.Node('MULTIPLICATION',
                left=Expression.Node('IDENTITY', value='y'),
                right=Expression.Node('NUMBER', value=2)))
        e = Expression(root=wrong, variables=['x', 'y'])
        self.assertGreater(self.f.expression_value(e), 0.0)


class ExpressionMutatorTest(unittest.TestCase):
    def setUp(self):
        root = Expression.Node('PLUS',
            Expression.Node('MULTIPLICATION',
                left=Expression.Node('IDENTITY', value='x'),
                right=Expression.Node('NUMBER', value=4)),
            Expression.Node('MULTIPLICATION',
                left=Expression.Node('IDENTITY', value='y'),
                right=Expression.Node('NUMBER', value=2)))
        self.f = Expression(root=root, variables=['x', 'y'])

    def test_number_mutation(self):
        mutator = ExpressionMutator(expression=self.f)
        mutator.number_mutation()
        point = {'x': 1, 'y': 2}
        original_value = self.f.value_in_point(point)
        mutated_value = mutator.expression.value_in_point(point)
        self.assertNotEqual(original_value, mutated_value)