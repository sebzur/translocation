# -*- coding: utf-8 -*-
from translocation.base import Chain, can_exist
from translocation.onedim import OneDimChain, Representation
from translocation.onedim import MC
import numpy

import math
import random
 
import Queue
import threading
import time
import sys
    
class Worker(threading.Thread):
 
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
            
            data = MC().run(job['length'], job['prob'], job['steps'])
            #data = [random.random(), random.random()]
            #self.save(data, job['length'], job['epsilon'], job['prob']['H'], job['steps'], '')
            # store the result

            self.result_queue.put(data)

    def save(self, data, length, epsilon, hernia, steps, postfix):
        filename = 'results/S%d_B%.2f_H%.2f_N%d_R%d%s' % (steps, epsilon, hernia, length, i, postfix)
        numpy.savetxt(filename, repeat)




class MuiltiMC(object):

    def save(self, data, length, epsilon, hernia, steps, index, postfix):
        filename = 'results/S%d_B%.2f_H%.2f_N%d_R%d%s' % (steps, epsilon, hernia, length, index, postfix)
        #filename = 'results/S%d_B%.2f_H%.2f_N%d%s' % (steps, epsilon, hernia, length, index, postfix)
        
        #handle = open(filename, 'a')
        numpy.savetxt(filename, data)
        #handle.close()

    def execute(self, length, epsilon, steps, repeats, num_processes=1):
        #B = numpy.e**(-0.5*epsilon)
        B = epsilon
        PROB = {'E': 1, 'M': 1, 'H': 0.5, 'B': 1.0/B, 'F': B, 'UF': B, 'UB': 1.0/B}

        # load up work queue
        work_queue = Queue.Queue()
        for repeat in range(repeats):
            work_queue.put({'length': length, 'steps': steps, 'prob': PROB})            


        # create a queue to pass to workers to store the results
        result_queue = Queue.Queue()

        # spawn workers
        for i in range(num_processes):
            worker = Worker(work_queue, result_queue)
            worker.start()

        # collect the results off the queue
        collected = 0
        while collected < repeats:
            result = result_queue.get(block=True)
            self.save(result, length, epsilon, PROB['H'], steps, collected, '.MC')
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
