import numpy
from kmc.sampler import Sampler


class Diffusion(Sampler):
    
    def initialize(self):
        self.time = 0
        self.cms_x = 0
        
    def sample(self, step, dt, old_cfg, new_cfg, *args, **kwargs):
        self.epsilon = old_cfg.kwargs.get('epsilon')
        self.reptons = old_cfg.kwargs.get('reptons')
        
        if step > old_cfg.polimer.reptons**3:
            self.time += dt
            self.cms_x += new_cfg.polimer.get_cms_coord()[0] - old_cfg.polimer.get_cms_coord()[0]
       
    @classmethod
    def merge(cls, results, steps, repeats, **kwargs):
        
        #filename = "/tmp/diffusion.dat"
        filename = "/home/sebzur/diffusion.dat"
        
        plik = open(filename, 'a')
        D = 0
        for idx, val in enumerate(results):
             vdrift = val.cms_x/val.time
             D += vdrift / (val.reptons * val.epsilon)
             
        D = D/len(results)    
        plik.write("%d  %.20f  %.20f\n" % (val.reptons, D, val.epsilon))
        plik.close()


class Trajectory(Sampler):
    
    def initialize(self):
        self.time = [0]
        self.cms_x = [0]
        
    def sample(self, step, dt, old_cfg, new_cfg, *args, **kwargs):
        self.epsilon = old_cfg.kwargs.get('epsilon')
        self.reptons = old_cfg.kwargs.get('reptons')
        
        self.time.append(self.time[-1] + dt)
        self.cms_x.append(self.cms_x[-1] + new_cfg.polimer.get_cms_coord()[0] - old_cfg.polimer.get_cms_coord()[0])
       
    @classmethod
    def merge(cls, results, steps, repeats, **kwargs):
        for i, result in enumerate(results):
            data = numpy.array(zip(result.time, result.cms_x))
            numpy.savetxt('/tmp/traj_%s' % i, data)
