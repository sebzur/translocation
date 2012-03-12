# -*- coding: utf-8 -*-
""" 
Sampluje rozkład slacków wewnątrz łańcucha.

Zadaniem samplera jest wygenerowanie rozkłądu prawdobodobieństwa znalezienia
luźnego linka, przy ustalonym połżeniu pora.
 

"""
import base
import numpy

class SlackDist(base.Sampler):
    def __init__(self, *args, **kwargs):
        super(SlackDist, self).__init__(*args, **kwargs)
        self.data = {}
        self.total_time = 0.0

    def sample(self, repeat, step, dt, current_state, new_state, connection):
        # Sprawdzam położenia pora
        if step >= self.steps/3:
            return 

        self.total_time += dt
        L = current_state.states.index('p')

        if not self.data.has_key(L):
            self.data[L] = {'dist': [numpy.zeros(L), numpy.zeros(len(current_state.states) - L -1)],
                       'fact': [numpy.zeros(L), numpy.zeros(len(current_state.states) - L -1)]
                       }

        cis = map(lambda x: dt if x == 'o' else 0, current_state.states[:L])
        trans = map(lambda x: dt if x == 'o' else 0, current_state.states[L+1:])

        self.data[L]['dist'][0] += numpy.array(cis)
        self.data[L]['fact'][0] += numpy.array(cis) == 1

        self.data[L]['dist'][1] += numpy.array(trans)
        self.data[L]['fact'][1] += numpy.array(trans) == 1


    @classmethod
    def merge(cls, samplers, repeats, steps, dimension, length, prob):
        summer = {}
        print 'Length is', length
        for L in range(length):
            summer[L] = numpy.zeros(length - 1)
        for sampler in samplers:
            for L, value in sampler.data.iteritems():
                summer[L] += numpy.array(list(sampler.data[L]['dist'][0]) + list(sampler.data[L]['dist'][1]))/sampler.total_time
        for L in summer:
            summer[L] /= len(samplers)
            x = numpy.arange(length-1)
            x[L:] -= 1
            numpy.savetxt('tmp/%s' % L, zip(x, summer[L].transpose()))
        print summer



