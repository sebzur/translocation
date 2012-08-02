# -*- coding: utf-8 -*-
from translocation import onedim, base
from translocation.samplers import current
import sys
from optparse import OptionParser
from kmc.parallel import ParallelMC
import numpy

parser = OptionParser()
parser.add_option('-n', '--length', type='int', help='Chain length (links)')
parser.add_option('-e', '--epsilon', type='float', help='Epsilon')
parser.add_option('-s', '--steps', type='int', help='MC steps to go')
parser.add_option('-r', '--runs', type='int', help='MC runs')
parser.add_option('-c', '--hernia', type='float', help="Hernia")
parser.add_option('-p', '--path', type='string', help="Result path")



if __name__=='__main__':
    (options, args) = parser.parse_args()
    #B = options.epsilon
    B = numpy.e**(0.5*options.epsilon)
    PROB = {'E': 1, 'M': 1, 'H': options.hernia, 'B': 1.0/B, 'F': B, 'UF': B, 'UB': 1.0/B}

    ParallelMC().run(prob=PROB, steps=options.steps, repeats=options.runs, run_cls=onedim.OneDimRun, smpl_classes=[current.IonCurrent], length=options.length, path=options.path, eps=options.epsilon)
    #ParallelMC().run(prob=PROB, steps=options.steps, repeats=options.runs, run_cls=onedim.OneDimRun, smpl_classes=[current.CurrentTrack], length=options.length)

