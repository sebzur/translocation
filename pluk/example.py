from optparse import OptionParser
from kmc.parallel import ParallelMC
from kmc.serial import SerialMC, System
from samplers import Diffusion, Trajectory

from base import *

parser = OptionParser()
parser.add_option('-s', '--steps', type='int', help='MC steps to go')
parser.add_option('-r', '--runs', type='int', help='MC runs')
parser.add_option('-n', '--reptons', type='int', help="Reptons")
parser.add_option('-l', '--link_length', type='int', help="Link length")
parser.add_option('-d', '--dim', type='int', help="Dim")
parser.add_option('-e', '--epsilon', type='float', help="Epsilon")
parser.add_option('-b', '--crossing', type='float', help="Crossing")
parser.add_option('-c', '--hernia', type='float', help="Hernia")

      

class MySerialMC(SerialMC):
    system = TestDynamics

if __name__=='__main__':
    (options, args) = parser.parse_args()
    # path is some extra argument, steps and repeats are required
    ParallelMC().run(steps=options.steps, repeats=options.runs, run_cls=MySerialMC, smpl_classes=[Diffusion], reptons=options.reptons, link_length=options.link_length, dim=options.dim, epsilon=options.epsilon, crossing=options.crossing, hernia=options.hernia)




