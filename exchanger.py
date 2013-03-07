__author__ = 'Stanislav Ushakov'

class SimpleRandomExchanger:
    """
    Class represents simple exchanger that simulates communicating wth the other
    nodes. Simply returns randomly generated lymphocytes.
    """
    def __init__(self, generator):
        self.generator = generator

    def set_lymphocytes_to_exchange(self, lymphocytes):
        """
        Set the lymphocytes using for exchange - these lymphocytes will
        be given to the other node when requested.
        """
        self.to_exchange = lymphocytes

    def get_lymphocytes(self):
        """
        Returns lymphocytes from the other node.
        In this class - simply randomly generated.
        """
        return self.generator()