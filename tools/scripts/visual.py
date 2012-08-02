# -*- coding: utf-8 -*-
from translocation.onedim import OneDimChain, Representation
import numpy
import sys


class Visualiser(object):
    def run(self, length, prob, steps):
        # -----------------------------
        cis = numpy.arange(0, length-1) 
        trans = numpy.array([])
        rpr = Representation(cis,trans)
        z = OneDimChain(rpr)
        # -----------------------------

        dT = 0.0
        dL = 0

        old_trans = z.get_cfg().trans.size
        data = []
        for i in range(steps):
            it = z.get_lifetime(prob)
            dT += it

            old_trans = z.get_cfg().cis

            print dT, it, '\t'.join(map(str, -z.get_cfg().cis)), '\t'.join(map(str,z.get_cfg().trans))
            z.reconfigure(PROB)

if __name__ == "__main__":
    # -----------------------------
    B = float(sys.argv[1])
    PROB = {'E': 1, 'M': 1, 'H': 0.5, 'B': 1.0/B, 'F': B, 'UF': B, 'UB': 1.0/B}
    # -----------------------------
    Visualiser().run(int(sys.argv[2]), PROB, int(sys.argv[3]))
