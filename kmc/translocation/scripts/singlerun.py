# -*- coding: utf-8 -*-
from translocation import onedim, base
from translocation.samplers import current
import sys
import numpy
import time
#from pylab import *

if __name__ == "__main__":
    # -----------------------------
    st = time.time()
    epsilon = float(sys.argv[2])
    #B = numpy.e**(0.5*epsilon)
    B = epsilon
    PROB = {'E': 1, 'M': 1, 'H': 0.5, 'B': 1.0/B, 'F': B, 'UF': B, 'UB': 1.0/B}
    #------------------------------
    z = onedim.OneDimRun().run(prob=PROB, steps=int(sys.argv[3]), smpl_classes=[current.Current], length=int(sys.argv[1])) 
    #hist(z[0].times, bins=100)
    #show()
    st = time.time() - st
    print  epsilon, z[0].distance/z[0].time, int(sys.argv[1]), st


