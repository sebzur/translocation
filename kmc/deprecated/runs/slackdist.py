# -*- coding: utf-8 -*-
import numpy
import sys
sys.path.append('/home/seba/codebase/MC_cleaning')
from chain import onedim, twodim
from stochastics import Translocation
from montecarlo_parallel import MonteCarlo
from samplers.slackdist import SlackDist

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def get_prob(B=1, H=0.0):
    #B = numpy.e**(-0.5*epsilon)
    prob = {'B': 1.0/B,'F': B,
            'UB': 1.0/B, 'UF': B, 
            'E': 1.0,
            'M': 1.0,
            'H': H,
            'C': 0.0}
    return prob

if __name__ == "__main__":

    length = 31
    dim = 1
    m_c = MonteCarlo([SlackDist]) # no samplers in testcase
    eig = m_c.run(get_prob(B=2,H=0.5), 300, 100000, length, dim)
    #eig = m_c.run(prob, 30, 100, length+1)
    #if rank == 0:
    #    translocation = Translocation(objects)
        #print eig
    #    print translocation.get_translocation_time(prob, eig)
