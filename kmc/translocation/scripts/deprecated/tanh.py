# -*- coding: utf-8 -*-
from translocation.base import Chain, can_exist
from translocation.onedim import OneDimChain, Representation
from translocation.onedim import MC
import numpy

import math
import random
 
import Queue
import multiprocessing
import time
import sys
    
class Worker(multiprocessing.Process):
 
    def __init__(self, work_queue, result_queue, *args, **kwargs):
 
        # base class initialization
        super(Worker, self).__init__(*args, **kwargs)
 
        # job management stuff
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.kill_received = False
        self.mc = MC()
 
 
    def run(self):
        while not self.kill_received:
            # get a task
            try:
                job = self.work_queue.get_nowait()
            except Queue.Empty:
                break
            
            data = self.runmc(job['length'], job['prob'], job['steps'])
            #data = [random.random(), random.random()]
            #self.save(data, job['length'], job['epsilon'], job['prob']['H'], job['steps'], '')
            # store the result

            print 'Putting dfata', data[-1]
            self.result_queue.put(data)

    def save(self, data, length, epsilon, hernia, steps, postfix):
        filename = 'results/S%d_B%.2f_H%.2f_N%d_R%d%s' % (steps, epsilon, hernia, length, i, postfix)
        numpy.savetxt(filename, repeat)

    def runmc(self, length, prob, steps):
        # -----------------------------
        cis = numpy.arange(0, length-1) 
        trans = numpy.array([])
        rpr = Representation(cis,trans)
        z = OneDimChain(rpr)
        # -----------------------------

        dT = 0.0
        dL = 0

        old_trans = z.get_cfg().trans.size
        adata = []
        for i in range(steps):
            it = z.get_lifetime(prob)
            dT += it
            # -----------------------------
            disp = z.get_cfg().trans.size - old_trans
            if disp in [1, -(z.get_cfg().length-1)]:
                dL += 1
            elif disp in [-1, z.get_cfg().length-1]:
                dL += -1
            # -----------------------------

            old_trans = z.get_cfg().trans.size

            j = dL/dT

            adata.append((dT, z.get_cfg().cis.size, dL,  j))
            #print (dT, z.get_cfg().cis.size, dL,  j)

            c, n =  z.reconfigure(prob)
        
        return adata



class MuiltiMC(object):

    def save(self, data, length, epsilon, hernia, steps, index, postfix):
        filename = 'results/S%d_B%.2f_H%.2f_N%d_R%d%s' % (steps, epsilon, hernia, length, index, postfix)
        #print 'Zapisuje cos co mam', data[-1], filename
        numpy.savetxt(filename, data)

    def execute(self, length, epsilon, steps, repeats, num_processes=1):
        #B = numpy.e**(-0.5*epsilon)
        B = epsilon
        PROB = {'E': 1, 'M': 1, 'H': 0.5, 'B': 1.0/B, 'F': B, 'UF': B, 'UB': 1.0/B}

        # load up work queue
        work_queue = multiprocessing.Queue()
        for repeat in range(repeats):
            work_queue.put({'length': length, 'steps': steps, 'prob': PROB})            


        # create a queue to pass to workers to store the results
        result_queue = multiprocessing.Queue()

        # spawn workers
        for i in range(num_processes):
            worker = Worker(work_queue, result_queue)
            worker.start()

        # collect the results off the queue
        collected = 0
        while collected < repeats:
            result = result_queue.get(block=True)
            #print 'Collected', collected, 'results of', repeats, 'in total.'
            #print 'REsult is', result[-1]
            self.save(list(result), length, epsilon, PROB['H'], steps, collected, '.MC')
            collected += 1
            #results.append(result)


if __name__ == "__main__":
    #for b in (0.01, 0.1, 1, 2, 5, 10, 20):
    #    print 'Processing EPS:', b
    # N, epsilon, steps, repeats, procesors
    MuiltiMC().execute(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    if 0:
        log = open('results/log', 'a')
        for n in (5, 9):
            for b in (0.01, 0.1, 1, 2, 5, 10, 20):
                log.write('Processing: N=%s, EPS=%s\n' % (n, b))
                MuiltiMC().execute(n, b, 100000, 64, 16)
        log.close()
