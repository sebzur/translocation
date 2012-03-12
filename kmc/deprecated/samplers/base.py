# -*- coding: utf-8 -*-

class Sampler(object):
    """ Bazowa klasa opisująca interfejs samplera. """

    def __init__(self, repeats, steps, length, dimension, prob, rank, period):
        """ Każdy sampler posiada zestaw danych opisujących symulację i jej
        podstawowe parametry. Definując klasy potomne powinniśmy pamiętać o 
        superowaniu.

        """
        self.repeats = repeats
        self.steps = steps
        self.rank = rank
        self.length = length
        self.prob = prob
        self.dimension = dimension
        self.period = period

    @classmethod
    def merge(cls, samplers, repeats, steps, dimension, length, prob, period):
        raise NotImplementedError

    def prepare_to_return(self):
        return None
