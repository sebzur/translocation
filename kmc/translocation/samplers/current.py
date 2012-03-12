# -*- coding: utf-8 -*-
from kmc import process
import numpy

class Current(process.Sampler):

    def __init__(self, *args, **kwargs):
        super(Current, self).__init__(*args, **kwargs)
        self.length = kwargs.get('length')
        self.distance = 0.0
        self.time = 0.0

    def sample(self, step, dt, old_cfg, new_cfg, connection):    

        self.time += dt
        
        if connection.get_rate() in ('B', 'UB'):
            self.distance -= 1

        if connection.get_rate() in ('F', 'UF'):
            self.distance += 1
            

    @classmethod
    def merge(cls, results, prob, steps, repeats, **kwargs):
        resu = numpy.array([r.distance/r.time for r in results])
        j_mean = resu.mean()
        j_std = resu.std()
        j_error = j_std/numpy.sqrt(repeats)
        postfix = ''
        pth_prefix = '/home/seba/codebase/kmc/translocation/scripts'
        #pth_prefix = '/home/sebzur/kmc/translocation/scripts'
        filename = '%s/results/S%d_H%.2f_N%d_C%d_R%d%s' % (pth_prefix, steps, prob['H'], kwargs.get('length'), 3, repeats, postfix)
        data_file = open(filename, 'a')
        eps = numpy.log(prob['F']) * 2.0
        data_file.write('%.10f\t%.10f\t%.10f\t%.10f\n' % (eps, j_mean, j_std, j_error))
        data_file.close()


class CurrentTrack(process.Sampler):

    def __init__(self, *args, **kwargs):
        super(CurrentTrack, self).__init__(*args, **kwargs)
        self.length = kwargs.get('length')
        self.distance = 0.0
        self.time = 0.0
        self.data = []

    def sample(self, step, dt, old_cfg, new_cfg, connection):    

        self.time += dt

        append = False
        if connection.get_rate() in ('B', 'UB'):
            self.distance -= 1
            append = True

        if connection.get_rate() in ('F', 'UF'):
            self.distance += 1
            append = True
            
        if append:
            self.data.append((self.time, self.distance, step))

    @classmethod
    def merge(cls, results, prob, steps, repeats, **kwargs):
        resu = numpy.array([r.distance/r.time for r in results])
        j_mean = resu.mean()
        j_std = resu.std()
        j_error = j_std/numpy.sqrt(repeats)
        postfix = ''
        pth_prefix = '/home/seba/codebase/kmc/translocation/scripts'
        #pth_prefix = '/home/sebzur/kmc/translocation/scripts'
        filename = '%s/results/S%d_H%.2f_N%d_C%d_R%d%s' % (pth_prefix, steps, prob['H'], kwargs.get('length'), 3, repeats, postfix)
        data_file = open(filename, 'a')
        eps = numpy.log(prob['F']) * 2.0
        data_file.write('%.10f\t%.10f\t%.10f\t%.10f\n' % (eps, j_mean, j_std, j_error))
        data_file.close()

        for i, r in enumerate(results):
            filename = '%s/results/S%d_H%.2f_N%d_C%d_R%d%s_track_%d' % (pth_prefix, steps, prob['H'], kwargs.get('length'), 3, repeats, postfix, i)
            numpy.savetxt(filename, r.data)
        
