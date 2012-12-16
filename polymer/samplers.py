import numpy
import os
from kmc.sampler import Sampler


class LinkCorrelation(Sampler):
    
    
    def __init__(self, steps, **kwargs):
        super(LinkCorrelation, self).__init__(steps, **kwargs)
        self.length = kwargs.get('cor_len')
        self.cor_sum = numpy.zeros(self.length)
        self.cor_numb = numpy.zeros(self.length)
    
    
    def find_tauts(self, cfg):
        begin_index = []
        ile = 0
        for idx in range(1, cfg.particles.number-2):
            if numpy.any(cfg.particles.positions[idx] != cfg.particles.positions[idx+1]):
               ile = ile + 1;
               begin_index.append(idx)
        
        return begin_index
    
    def correlation_el(self, vector_u, vector_v, n):
        self.cor_sum[n] = self.cor_sum[n] + numpy.dot(vector_u, vector_v)
        self.cor_numb[n] = self.cor_numb[n] + 1 
        
    def calculate(self, cfg):
        
        links = self.find_tauts(cfg)
        start = int(len(links) *0.5 +0.5)
        if start >= self.length+1 and len(links) >= 2 * self.length+1:
            left = links[:start+1]
            right = links[start:] 
            left.reverse()
            
            sides = [left, right]
            for tab in sides:
                ile = 0;
                idx_e = tab[1]
                idx_s = tab[0]
                vector_u = cfg.particles.positions[idx_e] - cfg.particles.positions[idx_s]
                self.correlation_el(vector_u, vector_u, ile)
                idx_s = idx_e
                for idx_e in tab[2:]:
                    ile = ile + 1
                    if ile >= self.length:
                        break
                    vector_v = cfg.particles.positions[idx_e] - cfg.particles.positions[idx_s]
                    self.correlation_el(vector_u, vector_v, ile)
                    idx_s = idx_e
        
    def get_correlation_result(self):
            return self.cor_sum / self.cor_numb
            
            
    def sample(self, step, dt, old_cfg, new_cfg, *args, **kwargs):
       
        if step > old_cfg.particles.number**3:
            self.calculate(old_cfg)

    @classmethod
    def merge(cls, results, steps, repeats, **kwargs):
        
        filename = os.path.join(kwargs.get('output'), 'link_correlation.dat')

        plik = open(filename, 'a')
        size = results[0].length
        correlation = numpy.zeros(size)
        
        
        for idx, val in enumerate(results):
            correlation = correlation + val.get_correlation_result()
            
        res = correlation/len(results)
        for idx, val in enumerate(res):
            plik.write("%.20f\t%.20f\n" % (idx, val))
        
        plik.close()
             
        
     
class DriftVelocity(Sampler):

    def initialize(self):
        self.time = 0
        self.cms_x = 0

    def sample(self, step, dt, old_cfg, new_cfg, *args, **kwargs):
        self.epsilon = old_cfg.kwargs.get('epsilon')
        self.particles = old_cfg.kwargs.get('particles')

        if step > old_cfg.particles.number**3:
            self.time += dt
            self.cms_x += new_cfg.particles.get_cms_coord()[0] - old_cfg.particles.get_cms_coord()[0]

    @classmethod
    def merge(cls, results, steps, repeats, **kwargs):

        filename = os.path.join(kwargs.get('output'), 'drift_vel.dat')

        plik = open(filename, 'a')
        vel = []
        for idx, val in enumerate(results):
             vdrift = val.cms_x/val.time
             vel.append(vdrift)

        vel = numpy.array(vel)
        vel_error = vel.std()/numpy.sqrt(vel.size)
        plik.write("%.20f\t%.20f\t%.20f\n" % (val.epsilon, vel.mean(), vel_error))
        plik.close()


class Diffusion(Sampler):
    
    def initialize(self):
        self.time = 0
        self.cms_x = 0
        
    def sample(self, step, dt, old_cfg, new_cfg, *args, **kwargs):
        self.epsilon = old_cfg.kwargs.get('epsilon')
        self.particles = old_cfg.kwargs.get('particles')
        
        if step > old_cfg.particles.number**3:
            self.time += dt
            self.cms_x += new_cfg.particles.get_cms_coord()[0] - old_cfg.particles.get_cms_coord()[0]
       
    @classmethod
    def merge(cls, results, steps, repeats, **kwargs):
        
        filename = os.path.join(kwargs.get('output'), 'diffusion.dat')
        
        plik = open(filename, 'a')
        D = []
        for idx, val in enumerate(results):
             vdrift = val.cms_x/val.time
             D.append(vdrift / (val.particles * val.epsilon))
             
        D = numpy.array(D)
        D_error = D.std()/numpy.sqrt(D.size)
        plik.write("%d\t%.20f\t%.20f\t%.20f\n" % (val.particles, D.mean(), D_error, val.epsilon))
        plik.close()


class Trajectory(Sampler):
    
    def initialize(self):
        self.time = [0]
        self.cms_x = [0]
        
    def sample(self, step, dt, old_cfg, new_cfg, *args, **kwargs):
        self.epsilon = old_cfg.kwargs.get('epsilon')
        self.reptons = old_cfg.kwargs.get('reptons')
        
        self.time.append(self.time[-1] + dt)
        self.cms_x.append(self.cms_x[-1] + new_cfg.polymer.get_cms_coord()[0] - old_cfg.polymer.get_cms_coord()[0])
       
    @classmethod
    def merge(cls, results, steps, repeats, **kwargs):
        for i, result in enumerate(results):
            data = numpy.array(zip(result.time, result.cms_x))
            numpy.savetxt('/tmp/traj_%s' % i, data)
