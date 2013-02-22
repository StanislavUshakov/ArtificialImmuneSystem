__author__ = 'Stanislav Ushakov'

import random
import math

class NotSupportedOperationError(Exception): pass

class Expression:
    """
    This class is used for representing expression tree.
    Root of the tree is stored in root field.
    List of all possible variable names is stored in variables field.
    All operations are stored in class field allowed_operations in the following form:
        NAME: (IsUnary, FunctionToGetValue, StringRepresentation)
    """
    allowed_operations = {
        'NUMBER': (True, lambda x: x),
        'IDENTITY': (True, lambda x: x),
        'PLUS': (False, lambda x, y: x + y, '+'),
        'MINUS': (False, lambda x, y: x - y, '-'),
        'MULTIPLICATION': (False, lambda x, y: x * y, '*'),
        'DIVISION': (False, lambda x, y: x / y if y != 0 else x / 0.000001, '/'),
        'SIN': (True, lambda x: math.sin(x), 'sin'),
        'COS': (True, lambda x: math.cos(x), 'cos')
    }

    class Node:
        """
        This class is used for representing node of the expression tree.
        left and right - references to the left and right subtrees respectively.
        operation - name of operation (dictionary key in Expression.allowed_operations).
        value - contains number if operation = 'NUMBER' or variable name if
        operation = 'IDENTITY'
        """
        def __init__(self, operation, left=None, right=None, value=None):
            """
            Initializes node of the expression tree.
            operation - name of the operation, must be passed only predefined value.
            If not - NotSupportedOperationError is thrown.
            Also left and right subtrees may be passed.
            value - only for 'NUMBER' and 'IDENTITY'.
            """
            if operation not in Expression.allowed_operations:
                raise NotSupportedOperationError(operation)
            self.operation = operation
            self.left = left
            self.right = right
            self.value = value

        def value_in_point(self, values):
            """
            Return value in the current node, calculated for provided
            values of the variables.
            values - dictionary containing values for all needed variables, e.g.
            {'x': 1, 'y': 2}
            """
            if self.operation =='NUMBER':
                return self.value
            if self.operation == 'IDENTITY':
                return values[self.value]

            op = Expression.allowed_operations[self.operation]
            if op[0]:
                return op[1](self.left.value_in_point(values))

            return op[1](self.left.value_in_point(values),
                self.right.value_in_point(values))

        def height(self):
            """
            Returns height of the tree which root is the current node.
            """
            if self.is_number() or self.is_variable():
                return 1
            if self.is_unary():
                return self.left.height() if self.left is not None else 0 + 1

            return max(self.left.height() if self.left is not None else 0,
                self.right.height() if self.right is not None else 0) + 1

        def is_number(self):
            """
            Returns True only if the current node represents a number.
            """
            return self.operation == 'NUMBER'

        def is_variable(self):
            """
            Returns True only if the current node represents a variable.
            """
            return self.operation == 'IDENTITY'

        def is_unary(self):
            """
            Returns True only if the current node represents an unary operation.
            Number and variable are not considered as unary operations.
            """
            return (Expression.allowed_operations[self.operation][0] and
                    self.operation != 'NUMBER' and self.operation != 'IDENTITY')

        def is_binary(self):
            """
            Returns True only if the current node represents a binary operations.
            """
            return not Expression.allowed_operations[self.operation][0]

        def simplify(self):
            """
            Simplifies the current node and all its subtrees according
            to the simple arithmetic rules.
            Return True only if the current node or at least one
            of its subtrees was modified during the simplification.
            """
            #TODO: add more rules

            #leave only 3 digits after decimal point
            if self.is_number():
                self.value = round(self.value * 1000) / 1000

            #calculate unary function for number
            if self.is_unary() and self.left.is_number():
                self.value = self.value_in_point({})
                self.operation = 'NUMBER'
                self.left = None
                return True

            #calculate binary function for two numbers
            if (self.is_binary() and self.left.is_number()
                and self.right.is_number()):
                self.value = self.value_in_point({})
                self.operation = 'NUMBER'
                self.left = self.right = None
                return True

            #calculate x / x
            if (self.is_binary() and
                    self.left.is_variable() and self.right.is_variable() and
                    self.left.value == self.right.value and self.operation == 'DIVISION'):
                self.value = 1
                self.operation = 'NUMBER'
                self.left = self.right = None
                return True

            result = False
            if self.left is not None:
                result_left = self.left.simplify()
                result = result or result_left
            if self.right is not None:
                result_right = self.right.simplify()
                result = result or result_right

            return result

        def __str__(self):
            """
            Returns string representation of tree which root is the
            current node.
            All binary operation has a pair of parentheses.
            """
            if self.is_number() or self.is_variable():
                return str(self.value) if self.value is not None else 'None'

            if self.is_unary():
                return Expression.allowed_operations[self.operation][2] + '(' +\
                       (str(self.left) if self.left is not None else 'None') + ')'

            if self.is_binary():
                return '(' + (str(self.left) if self.left is not None else 'None') +\
                       ' ' + Expression.allowed_operations[
                             self.operation][2] + ' ' +\
                       (str(self.right) if self.right is not None else 'None') + ')'

        def __repr__(self):
            """
            Doesn't return valid Python expression.
            Returns the same string representation as __str__ does.
            """
            return str(self)

    @classmethod
    def get_unary_operations(cls):
        """
        Returns list of unary operations.
        Number and variable are not unary operations
        """
        return [x for x in Expression.allowed_operations
                if Expression.allowed_operations[x][0] and
                   x != 'NUMBER' and x != 'IDENTITY']

    @classmethod
    def get_binary_operations(cls):
        """
        Returns list of all possible binary operations
        """
        return [x for x in Expression.allowed_operations
                if not Expression.allowed_operations[x][0]]

    @classmethod
    def generate_number(cls):
        """
        Returns randomly generated number in [-100, 100]
        """
        return (random.randint(-10, 10) / random.random() + 0.01) % 100

    @classmethod
    def generate_operator(cls, only_binary:bool=False):
        """
        Returns randomly selected allowed operations.
        The possibility of a binary operation is higher than possibility
        of an unary operation.
        IF isBinary = True returns binary operation
        """
        if only_binary or random.random() < 0.6:
            return random.choice(Expression.get_binary_operations())
        else:
            return random.choice(Expression.get_unary_operations() +
                                 Expression.get_binary_operations())

    @classmethod
    def generate_random(cls, max_height, variables):
        """
        Generates random expression tree which height is not more than given
        max_height value with variable names from variables list.
        """
        root = Expression.Node(Expression.generate_operator(only_binary=True))
        current = [root]
        while len(current) > 0:
            node = current.pop(0)
            if node.is_number():
                node.value = Expression.generate_number()
                continue

            if node.is_variable():
                node.value = random.choice(variables)
                continue

            if node.is_unary():
                node.left = Expression.Node(Expression.generate_operator())
                if root.height() > max_height:
                    node.left = None
                else:
                    current.append(node.left)

            if node.is_binary():
                node.left = Expression.Node(Expression.generate_operator())
                node.right = Expression.Node(Expression.generate_operator())
                if root.height() > max_height:
                    node.left = None
                    node.right = None
                else:
                    current.append(node.left)
                    current.append(node.right)

        #turn all leaves into numbers or variables
        leaves = []
        def traverse_tree(node):
            if node.is_number() or node.is_variable():
                return
            if node.is_unary():
                if node.left is None:
                    leaves.append(node)
                else:
                    traverse_tree(node.left)
            if node.is_binary():
                if node.left is None:
                    leaves.append(node)
                else:
                    traverse_tree(node.left)
                if node.right is not None:
                    traverse_tree(node.right)
        traverse_tree(root)

        for node in leaves:
            if random.random() > 0.5:
                node.operation = 'NUMBER'
                node.value = Expression.generate_number()
            else:
                node.operation = 'IDENTITY'
                node.value = random.choice(variables)

        return Expression(root=root, variables=variables)

    def __init__(self, root, variables):
        """
        Initializes expression tree with the given root and a list
        of possible variables.
        """
        self.root = root
        self.variables = variables

    def value_in_point(self, values):
        """
        Returns value calculated for given values of variables.
        """
        return self.root.value_in_point(values)

    def simplify(self):
        """
        Simplifies entire expression tree.
        While we have changes in the tree - call simplify.
        """
        result = self.root.simplify()
        while result:
            result = self.root.simplify()

    def __str__(self):
        """
        Returns the string representation of the expression tree.
        Simply calls str for the root node.
        """
        return str(self.root)
