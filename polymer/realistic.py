from optparse import OptionParser
from kmc.parallel import ParallelMC
from kmc.serial import SerialMC, System
from samplers import Diffusion, Trajectory, DriftVelocity
from dynamics import RealisticModel

parser = OptionParser()
parser.add_option('-s', '--steps', type='int', help='MC steps to go')
parser.add_option('-r', '--runs', type='int', help='MC runs')
parser.add_option('-p', '--particles', type='int', help="Particles")
parser.add_option('-l', '--link_length', type='int', help="Link length")
parser.add_option('-e', '--epsilon', type='float', help="Epsilon")
parser.add_option('-b', '--crossing', type='float', help="Crossing")
parser.add_option('-c', '--hernia', type='float', help="Hernia")
parser.add_option('-k', '--kappa', type='float', help="Kappa")
parser.add_option('-x', '--exclusion', type='float', help="Exclusion")
parser.add_option('-o', '--output', type='str', help="Output dir")


class PolymerSerialMC(SerialMC):
    system = RealisticModel

if __name__=='__main__':
    (options, args) = parser.parse_args()

    # Precalculating the simulation length
    thermalization = options.particles ** 3
    total_steps = thermalization + options.steps

    # path is some extra argument, steps and repeats are required
    ParallelMC().run(steps=total_steps, repeats=options.runs, run_cls=PolymerSerialMC, smpl_classes=[DriftVelocity], particles=options.particles, link_length=options.link_length, epsilon=options.epsilon, crossing=options.crossing, hernia=options.hernia, kappa=options.kappa, el=options.exclusion, output=options.output)




