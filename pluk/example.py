from optparse import OptionParser
from kmc.parallel import ParallelMC
from kmc.serial import SerialMC, System
from kmc.sampler import Sampler

from base import *

parser = OptionParser()
parser.add_option('-s', '--steps', type='int', help='MC steps to go')
parser.add_option('-r', '--runs', type='int', help='MC runs')
parser.add_option('-p', '--reptons', type='int', help="Reptons")
parser.add_option('-l', '--link_length', type='int', help="Link length")
parser.add_option('-d', '--dim', type='int', help="Dim")





class MySampler(Sampler):
    
    def initialize(self):
        self.time = 0
        self.cms_x = 0
        
    def sample(self, step, dt, old_cfg, new_cfg, *args, **kwargs):
        if step > old_cfg.polimer.reptons**3:
            self.time += dt
            self.cms_x += new_cfg.polimer.get_cms_coord()[0] - old_cfg.polimer.get_cms_coord()[0]
       
    @classmethod
    def merge(cls, results, steps, repeats, **kwargs):
        
        plik = open('/tmp/result.dat','w')
        for idx, val in enumerate(results):
            plik.write("%d  %f  %f\n" % (idx, val.time, val.cms_x))
        plik.close()
       

class MySerialMC(SerialMC):
    system = TestDynamics

if __name__=='__main__':
    (options, args) = parser.parse_args()
    # path is some extra argument, steps and repeats are required
    ParallelMC().run(steps=options.steps, repeats=options.runs, run_cls=MySerialMC, smpl_classes=[MySampler], reptons=options.reptons, link_length=options.link_length, dim=options.dim)



