# -*- coding: utf-8 -*-
import copy

class Sampler(object):
    
    def __init__(self, prob, steps, **kwargs):
        self.prob = prob
        self.steps = steps

    def sample(self, step, dt, old_cfg, new_cfg, connection):
        pass

    def sample(self, step, dt, old_cfg, new_cfg, connection):
        """" Use the data provided in args and do something! """
        raise NotImplementedError

    @classmethod
    def merge(cls, results, prob, steps, repeats, **kwargs):
        """ This will be called at the end of calculations """
        raise NotImplementedError

class MCRun(object):
    
    def generate_state(self, **kwargs):
        raise NotImplementedError

    def on_exit(self, samplers, step, dt, old_cfg, new_cfg, connection):
        raise NotImplementedError

    def run(self, prob, steps, smpl_classes, **kwargs):
        samplers = [cls(prob, steps, **kwargs) for cls in smpl_classes]
        walker = self.generate_state(**kwargs)
        for step in range(steps):
            dt = walker.get_lifetime(prob)
            old_cfg = copy.deepcopy(walker.get_cfg())
            connection, new_cfg =  walker.reconfigure(prob)
            self.sample(samplers, step, dt, old_cfg, new_cfg, connection)
        self.on_exit(samplers, step, dt, old_cfg, new_cfg, connection)
        return samplers
            

    def sample(self, samplers, step, dt, old_cfg, new_cfg, connection):
        """ Sygnalizuje wszystkim samplerom zawartym w liście 'samplers', że można by coś
         w końcu policzyć - wywołuje po kolei każdego, podając mu na wejściu informacje.

         Każdy z samplerów powinien lokalnie zarządzać pamięcią - obiekty te są lokalnie 
         (w sensie na poziomie wątku MPI) tworzone i trzymane przez cały czas pracy symulacji.

         """
        for sampler in samplers:
            sampler.sample(step, dt, old_cfg, new_cfg, connection)


