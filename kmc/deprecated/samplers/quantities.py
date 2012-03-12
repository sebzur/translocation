# -*- coding: utf-8 -*-
""" 
Wylicza current - generuje zestaw plików dla każdegó powtórzenia MC,
w kazdym pliku znajduje się [t L, CL], gidze t to kolejny czas, L to
przebieg pora a LC kumulownay przebieg.

Analize można wykoniać:
python ./tools/merge.py tmp/current/15_sisters_ok/sisters_1D_R160_S1000000_B2.00_H0.50_N 15 15 160


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

class TSData(base.Sampler):
    def __init__(self, *args, **kwargs):
        super(TSData, self).__init__(*args, **kwargs)
        # mierzy całkowity czas w danym powtórzeniu
        self.total_time = 0.0
        self.pore_position = [(0, 0, 0)]
        self.inc = 1.0

    def sample(self, repeat, step, dt, current_state, new_state, connection):
        #if step >= self.steps/3:
        #    return 

        self.total_time += dt

        cpp = current_state.states.index('p')
        ppp = new_state.states.index('p')
        disp = cpp - ppp
        
        if disp in [1, -(self.length-1)]:
            self.pore_position.append((self.total_time,  self.pore_position[-1][1] + self.inc, cpp))
        elif disp in [-1, self.length-1]:
            self.pore_position.append((self.total_time,  self.pore_position[-1][1] - self.inc, cpp))

    @classmethod
    def merge(cls, samplers, repeats, steps, dimension, length, prob, period):
        #RULE = "sisters"
        #DIR_NAME = "%s_configs/%d" % (RULE, self.length)
        fits = []
        print samplers
        for j, sampler in enumerate(samplers):
            #print sampler, sampler.total_time

            #file_name = 'tmp/%s/traj_%dD_%s_R%d_S%d_B%.2f_H%.2f_N%d_cR%d' % (DIR_NAME, dimension, RULE, repeats, steps, prob['F'], prob['H'], length, j)
            
            file_name = 'tmp/transistor/sisters_%dD_R%d_S%d_B%.2f_H%.2f_N%d_period_%d_cR%d' % (dimension, repeats, steps, prob['F'], prob['H'], length, period, j)
            numpy.savetxt(file_name, sampler.pore_position)

