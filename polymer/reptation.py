from optparse import OptionParser
from kmc.parallel import ParallelMC
from kmc.serial import SerialMC, System
from samplers import Diffusion, Trajectory
from dynamics import ReptationModel

parser = OptionParser()
parser.add_option('-s', '--steps', type='int', help='MC steps to go')
parser.add_option('-r', '--runs', type='int', help='MC runs')
parser.add_option('-p', '--particles', type='int', help="Particles")
parser.add_option('-l', '--link_length', type='int', help="Link length")
parser.add_option('-e', '--epsilon', type='float', help="Epsilon")
parser.add_option('-o', '--output', type='str', help="Output dir")


class PolymerSerialMC(SerialMC):
    system = ReptationModel

if __name__=='__main__':
    (options, args) = parser.parse_args()

    # Precalculating the simulation length
    thermalization = options.particles ** 3
    total_steps = thermalization + options.steps

    # path is some extra argument, steps and repeats are required
    ParallelMC().run(steps=total_steps, repeats=options.runs, run_cls=PolymerSerialMC, smpl_classes=[Diffusion], particles=options.particles, link_length=options.link_length, epsilon=options.epsilon, hernia=0, output=options.output)




