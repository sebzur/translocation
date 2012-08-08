import numpy
import os
from kmc.sampler import Sampler


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
