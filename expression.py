__author__ = 'Stanislav Ushakov'

import random
import math

class NotSupportedOperationError(Exception): pass

class Operation:
    """
    Class represents single operation.
    It isn't supposed to create instances of Operation class in code.
    Operations.{OPERATION} must be used instead.
    is_unary - True, if operation is unary
    action - function that returns result of this operation (1 or 2 arguments)
    string_representation - for printing expressions
    """
    def __init__(self, operation_type, action, string_representation=''):
        self._operation_type = operation_type
        self.action = action
        self.string_representation = string_representation

    def is_number(self):
        return self._operation_type == Operations._number

    def is_variable(self):
        return  self._operation_type == Operations._variable

    def is_unary(self):
        return  self._operation_type == Operations._unary_operation

    def is_binary(self):
        return  self._operation_type == Operations._binary_operation

    #ugly stuff for serializing

    _dict_key = 'operation'

    def __getstate__(self):
        """
        Because of problems with pickle, have to override this method.
        """
        if self._operation_type == Operations._number:
            return {self._dict_key : 'number'}
        if self._operation_type == Operations._variable:
            return {self._dict_key : 'variable'}
        return {self._dict_key : self.string_representation}

    def __setstate__(self, state):
        """
        Initializes operation where unpickling
        """
        if state[self._dict_key] == 'number':
            operator = Operations.NUMBER
        elif state[self._dict_key] == 'variable':
            operator = Operations.IDENTITY
        elif state[self._dict_key] == '+':
            operator = Operations.PLUS
        elif state[self._dict_key] == '-':
            operator = Operations.MINUS
        elif state[self._dict_key] == '*':
            operator = Operations.MULTIPLICATION
        elif state[self._dict_key] == '/':
            operator = Operations.DIVISION
        elif state[self._dict_key] == 'sin':
            operator = Operations.SIN
        elif state[self._dict_key] == 'cos':
            operator = Operations.COS
        self._init_from_operation(operator)

    def _init_from_operation(self, operation):
        self._operation_type = operation._operation_type
        self.action = operation.action
        if hasattr(operation, 'string_representation'):
            self.string_representation = operation.string_representation

class Operations:
    """
    Class represents all possible operations.
    """
    _number = 0
    _variable = 1
    _unary_operation = 2
    _binary_operation = 3

    NUMBER = Operation(operation_type=_number,
                       action=(lambda x: x))
    IDENTITY = Operation(operation_type=_variable,
                         action=(lambda x: x))
    PLUS =  Operation(operation_type=_binary_operation,
                      action=(lambda x, y: x + y),
                      string_representation='+')
    MINUS = Operation(operation_type=_binary_operation,
                      action=(lambda x, y: x - y),
                      string_representation='-')
    MULTIPLICATION = Operation(operation_type=_binary_operation,
                               action=(lambda x, y: x * y),
                               string_representation='*')
    DIVISION = Operation(operation_type=_binary_operation,
                         action=(lambda x, y: x / y if y != 0 else x / 0.000001),
                         string_representation='/')
    SIN = Operation(operation_type=_unary_operation,
                    action=(lambda x: math.sin(x)),
                    string_representation='sin')
    COS = Operation(operation_type=_unary_operation,
                    action=(lambda x: math.cos(x)),
                    string_representation='cos')

    @classmethod
    def get_unary_operations(cls):
        """
        Returns list of unary operations.
        Number and variable are not unary operations
        """
        return [Operations.SIN, Operations.COS]

    @classmethod
    def get_binary_operations(cls):
        """
        Returns list of all possible binary operations
        """
        return [Operations.PLUS, Operations.MINUS, Operations.MULTIPLICATION, Operations.DIVISION]

class Expression:
    """
    This class is used for representing expression tree.
    Root of the tree is stored in root field.
    """

    class Node:
        """
        This class is used for representing node of the expression tree.
        left and right - references to the left and right subtrees respectively.
        operation - Operation object.
        value - contains number if operation = NUMBER or variable name if
        operation = IDENTITY
        """
        def __init__(self, operation, left=None, right=None, value=None):
            """
            Initializes node of the expression tree.
            operation - Operation object.
            If not - NotSupportedOperationError is thrown.
            Also left and right subtrees may be passed.
            value - only for NUMBER and IDENTITY.
            """
            if not isinstance(operation, Operation):
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
            if self.is_number():
                return self.value
            if self.is_variable():
                return values[self.value]

            if self.is_unary():
                return self.operation.action(self.left.value_in_point(values))

            return self.operation.action(self.left.value_in_point(values),
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
            return self.operation.is_number()

        def is_variable(self):
            """
            Returns True only if the current node represents a variable.
            """
            return self.operation.is_variable()

        def is_unary(self):
            """
            Returns True only if the current node represents an unary operation.
            Number and variable are not considered as unary operations.
            """
            return self.operation.is_unary()

        def is_binary(self):
            """
            Returns True only if the current node represents a binary operations.
            """
            return self.operation.is_binary()

        def simplify(self, accuracy=0.001):
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
                self.operation = Operations.NUMBER
                self.left = None
                return True

            #calculate binary function for two numbers
            if (self.is_binary() and self.left.is_number() and
                    self.right.is_number()):
                self.value = self.value_in_point({})
                self.operation = Operations.NUMBER
                self.left = self.right = None
                return True

            #calculate x / x
            if (self.is_binary() and
                    self.left.is_variable() and self.right.is_variable() and
                    self.left.value == self.right.value and self.operation == Operations.DIVISION):
                self.value = 1
                self.operation = Operations.NUMBER
                self.left = self.right = None
                return True

            #calculate x - x
            if (self.is_binary() and
                    self.left.is_variable() and self.right.is_variable() and
                    self.left.value == self.right.value and self.operation == Operations.MINUS):
                self.value = 0
                self.operation = Operations.NUMBER
                self.left = self.right = None
                return True

            #calculate x * 1 and x / 1
            if (self.is_binary() and
                    self.right.is_number() and abs(self.right.value - 1) < accuracy and
                    (self.operation == Operations.DIVISION or self.operation == Operations.MULTIPLICATION)):
                self._init_with_node(self.left)
                self.simplify()
                return True

            #calculate 1 * x
            if (self.is_binary() and
                    self.left.is_number() and abs(self.left.value - 1) < accuracy and
                    self.operation == Operations.MULTIPLICATION):
                self._init_with_node(self.right)
                self.simplify()
                return True

            result = False
            if self.left is not None:
                result_left = self.left.simplify()
                result = result or result_left
            if self.right is not None:
                result_right = self.right.simplify()
                result = result or result_right

            return result

        def _init_with_node(self, node):
            self.operation = node.operation
            self.value = node.value
            self.left = node.left
            self.right = node.right

        def __str__(self):
            """
            Returns string representation of tree which root is the
            current node.
            All binary operation has a pair of parentheses.
            """
            if self.is_number() or self.is_variable():
                return str(self.value)

            if self.is_unary():
                return self.operation.string_representation + '(' +\
                       (str(self.left) if self.left is not None else 'None') + ')'

            if self.is_binary():
                return '(' + (str(self.left) if self.left is not None else 'None') +\
                       ' ' + self.operation.string_representation + ' ' +\
                       (str(self.right) if self.right is not None else 'None') + ')'

        def __repr__(self):
            """
            Doesn't return valid Python expression.
            Returns the same string representation as __str__ does.
            """
            return str(self)

    @classmethod
    def generate_number(cls):
        """
        Returns randomly generated number in [-100, 100]
        """
        return (random.random() - 0.5) * 200

    @classmethod
    def generate_operator(cls, only_binary:bool=False):
        """
        Returns randomly selected allowed operations.
        The possibility of a binary operation is higher than possibility
        of an unary operation.
        IF isBinary = True returns binary operation
        """
        if only_binary or random.random() < 0.75:
            return random.choice(Operations.get_binary_operations())
        else:
            return random.choice(Operations.get_unary_operations() +
                                 Operations.get_binary_operations())

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
                node.operation = Operations.NUMBER
                node.value = Expression.generate_number()
            else:
                node.operation = Operations.IDENTITY
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
        while self.root.simplify(): pass

    def __str__(self):
        """
        Returns the string representation of the expression tree.
        Simply calls str for the root node.
        """
        return str(self.root)
