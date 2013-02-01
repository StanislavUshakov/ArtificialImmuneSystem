__author__ = 'Stanislav Ushakov'

import unittest

from expression import Expression, NotSupportedOperationError

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
                left=Expression.Node('IDENTITY',left=None, right=None, value='x'),
                right=Expression.Node('IDENTITY',left=None, right=None, value='y'))
        result = node.value_in_point({'x': 2, 'y': 1})
        self.assertEqual(result, 1.0)

    def test_simplify(self):
        node = Expression.Node('MINUS',
            left=Expression.Node('NUMBER',left=None, right=None, value=2),
            right=Expression.Node('NUMBER',left=None, right=None, value=2))
        result = node.simplify()
        self.assertEqual(result, True)
        self.assertEqual(node.left, None)
        self.assertEqual(node.right, None)
        self.assertEqual(node.value, 0.0)