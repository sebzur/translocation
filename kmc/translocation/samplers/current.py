# -*- coding: utf-8 -*-
from kmc import process
import numpy



class IonCurrent(process.Sampler):

    def __init__(self, *args, **kwargs):
        super(IonCurrent, self).__init__(*args, **kwargs)
        self.length = kwargs.get('length')
        self.distance = 0.0
        self.time = 0.0
        self.cumm_time=0.0
        self.cumm_current=0;

    def sample(self, step, dt, old_cfg, new_cfg, connection):    
        self.time += dt
        if step < 60000:
            return
        cis = new_cfg.cis
        trans = new_cfg.trans
      
        if cis.size:
            size = cis.max()
        else:
            size=0
            
        tab_cis = numpy.zeros(size+2)
        
        
        if trans.size:
            size = trans.max()
        else:
            size=0
        
        tab_trans = numpy.zeros(size+2)
        tab_cis[0]=1
        tab_trans[0]=1
        
        for i in cis:
            tab_cis[i] += 1
            
        for i in trans:
            tab_trans[i] += 1
        
        current_cis = 0
        current_trans = 0
        
        correct_cis = tab_cis[::-1]
        
        delta_cis = correct_cis[1:]- correct_cis[:-1]
        delta_trans = tab_trans[1:]- tab_trans[:-1]
        current_cis = numpy.exp(delta_cis).sum()
        current_trans =  numpy.exp(delta_trans).sum()
        current_bias = numpy.exp(2*0.5)*numpy.exp(tab_trans[0]- correct_cis[-1])
        
        current = (current_cis + current_trans + current_bias)/(current_cis.size + current_trans.size +2 )
        if connection.get_rate() in ('UF', 'UB'):
            print self.time, "  ", self.cumm_current/self.cumm_time
            self.cumm_current = 0
            self.cumm_time = 0
            
        self.cumm_current += current
        self.cumm_time += dt
        
        

    @classmethod
    def merge(cls, results, prob, steps, repeats, **kwargs):
        return
        resu = numpy.array([r.distance/r.time for r in results])
        j_mean = resu.mean()
        j_std = resu.std()
        j_error = j_std/numpy.sqrt(repeats)
        postfix = ''
        pth_prefix = kwargs.get('path')
        filename = '%s/results/S%d_H%.2f_N%d_C%d_R%d%s' % (pth_prefix, steps, prob['H'], kwargs.get('length'), 3, repeats, postfix)
        data_file = open(filename, 'a')
        eps = numpy.log(prob['F']) * 2.0
        data_file.write('%.10f\t%.10f\t%.10f\t%.10f\n' % (eps, j_mean, j_std, j_error))
        data_file.close()



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
        pth_prefix = kwargs.get('path')
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
        
