# -*- coding: utf-8 -*-
import numpy
from chain import onedim, twodim
from stochastics import Translocation
from montecarlo_parallel import MonteCarlo

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

class Simlengthparams(MonteCarlo):
    def simlengthparams(self, probabilities, length):
        translocation = Translocation(self.objects)
        #for total_steps in range(10000, 10000000, 10000):
        for total_steps in range(100, 1000, 100):
            for repeats in range(1, 100, 1):
                steps = total_steps/repeats
                eigenvector = self.run(probabilities, repeats, steps, length)
                if rank == 0:
                    print 'Processing repeats: %d, steps: %s' % (repeats, steps)
                    data_file = open('tmp/steps_repeats.txt', 'a')
                    eigen_file = open('tmp/eigendata/eigendata_%d_%d.txt' % (repeats, steps), 'w')
                    for key in eigenvector:
                        eigen_file.write('%s\t%.20f\n' % (key, eigenvector[key])) 
                    eigen_file.close()
                    dx, vel, t_time, thr = translocation.get_translocation_time(probabilities, eigenvector)
                    print '=' * 10
                    print 'Collected:'
                    print '\t Thr:', thr, thr.mean(), thr.std()
                    print '=' * 10
                    data_row = "%d\t%d\t%.10f\t%.10f\t%.10f\t%.10f\t%.10f" % (repeats, steps, dx, vel.mean(), t_time.mean(), thr.mean(), thr.std())
                    data_file.write(data_row + '\n')
                    data_file.close()

class GoForLengthDistributions(MonteCarlo):
    def goforlength(self, probabilities):
        for length in [20, 40]:
            for dim in [1, 2]:
                repeats = 32
                steps = 10000000
                self.run(probabilities, repeats, steps, length, dim)

class GoForLength(MonteCarlo):
    def goforlength(self, probabilities):
        translocation = Translocation(self.objects)
        for length in range(3,11):
            repeats = 124
            steps = 1000000
            eigenvector = self.run(probabilities, repeats, steps, length)
            if rank == 0:
                print 'Processing length: %d' % (length)
                data_file = open('tmp/vsl.txt', 'a')
                dx, vel, t_time = translocation.get_translocation_time(probabilities, eigenvector)
                data_row = "%d\t%.10f\t%.10f\t%.10f" % (length, dx, vel.mean(), t_time.mean())
                data_file.write(data_row + '\n')
                data_file.close()

class GoForLengthTest(MonteCarlo):
    def goforlength(self, probabilities):
        translocation = Translocation(self.objects)
        repeats = 1
        for steps in range(1000, 100000, 10):
            for length in range(2,10):
                eigenvector = self.run(probabilities, repeats, steps, length)
                if rank == 0:
                    print 'Processing length: %d' % (length)
                    data_file = open('tmp/vsl_%d.txt' % steps, 'a')
                    dx, vel, t_time = translocation.get_translocation_time(probabilities, eigenvector)
                    data_row = "%d\t%.10f\t%.10f\t%.10f" % (length, dx, vel.mean(), t_time.mean())
                    data_file.write(data_row + '\n')
                    data_file.close()


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
    processor = GoForLengthDistributions()
    for B, H in ((2, 0.5), (2, 0.0), (1.1, 0.5), (1.1, 0.0)):
        processor.goforlength(get_prob(B, H))



