import numpy


class Particles(object):
    def __init__(self, nparticles, dim, *args, **kwargs):
        self.dim = dim
        self.number = nparticles
        self.positions = numpy.zeros((nparticles, dim))
   
    def get_neighbours_idx(self, repton_id):
        
        if repton_id == 0:
            tab = [0, 1]
        elif repton_id == self.number - 1:
            tab = [repton_id-1, repton_id]
        else:   
            tab = [repton_id-1, repton_id, repton_id+1]
            
        return tab

    def get_cms_coord(self):
        return self.positions.sum(axis=0)/self.positions.shape[0]

    def validate(self):
        """ Validates polymer configuration """
        if numpy.any(numpy.abs((self.positions[1:] - self.positions[:-1]).sum(axis=1)) > 1):
            raise ValueError("Invalid configuration")
    
    
class Translation(object):
    """Lattice base class"""
    def __init__(self):
        self._get_trans_count = self.get_translations().shape[0]

    def get_translations(self):
        """ Returns all possible tranlations, note, that this will define
        the latice also.
        """
        raise NotImplementedError
    
    def get_dim(self):
        return self.get_translations().shape[1]
        
    def get_initial_translations(self):
        """ sometimes some transletions can't be used to create polimer - [-1,1]"""
        return self.get_translations()
    
    def get_trans_count(self):
        return self._get_trans_count
        #return self.get_translations().shape[0]
        
    def get_translation(self, idx):
        return self.get_translations()[idx]

        

class Rule(object):
    """ Base class"""
    def __init__(self, particles_obj, lattice , *args, **kwargs):
        self.particles = particles_obj
        self.lattice = lattice
        self.rate = 1
        self.initialize(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        pass
    
    def get_rate(self, particle_id, trans_id, *args, **kwargs):
        raise NotImplementedError
       
    def get_update_list(particle_id, trans_id, *args, **kwargs):
        raise NotImplementedError
       



class Dynamics(object):
    """Dynamics - base class"""
    lattice = None
    rules_classes = []
    particles_class = None
    
    def __init__(self, *args, **kwargs):
        
        self.kwargs = kwargs
        self.args = args
        particles_number = kwargs.get('particles')
        
        dim = self.lattice.get_dim()
        
        self.rules = []
        self.particles = self.particles_class(particles_number, dim , *args, **kwargs)
        
        self.initialize_rules(*args, **kwargs)
        self.initialize_particles(*args, **kwargs)
        
        self.motion_matrix = numpy.zeros(particles_number * self.lattice.get_trans_count())
        self.motion_matrix.fill(1)
        self.cumulative_prob = self.motion_matrix.cumsum()
        
        #prepare first probability matrix and cumulaive sum
        self.find_all_translations()
        
    
    def initialize_particles(self, *args, **kwargs):
        raise NotImplementedError
    
    def initialize_rules(self, *args, **kwargs):
        for idx, rule in enumerate(self.rules_classes):
            self.rules.append(rule(self.particles, self.lattice, *args, **kwargs))
   
    def get_lifetime(self, *args, **kwargs):
        cum_prob = self.cumulative_prob[-1]
        random = numpy.random.uniform(low=0.0000000001, high=1)
        return -1.0*numpy.log(random)/cum_prob
    
        
    def reconfigure(self, *args, **kwargs):
        rand_nr = numpy.random.rand() * self.cumulative_prob[-1]
       
        for idx, prob in enumerate(self.cumulative_prob):
            if rand_nr <= prob:
                trans_id, particle_id = divmod(idx, self.particles.number)
                t_vect = self.lattice.get_translation(trans_id) 
                break
                
        self.particles.positions[particle_id] += t_vect
        self.update(particle_id, trans_id)
        
        
    def update(self, particle_id, trans_id):
        
        update_list = [ 0 for i in xrange(self.particles.number)]
        for rule in self.rules:
           for particle_idx in rule.get_update_list(particle_id, trans_id):
                update_list[particle_idx] = 1
        
        #updarte motion_matrix
        for trans_idx in xrange(0, self.lattice.get_trans_count()):
            for particle_idx, val in enumerate(update_list):
                if val == 1:
                    idx = self._get_coordinate(trans_idx, particle_idx )
                    self.motion_matrix[idx] = 1
                       
        for particle_idx, val in enumerate(update_list):
            if val ==1:
                for trans_idx in xrange(0, self.lattice.get_trans_count()):
                    rate = 1
                    for rule in self.rules:
                        rate = rate * rule.get_rate(particle_idx, trans_idx)
                        if rate == 0:
                            break
                    idx = self._get_coordinate(trans_idx, particle_idx)
                    self.motion_matrix[idx] = self.motion_matrix[idx] * rate
                        
        self.cumulative_prob = self.motion_matrix.cumsum()
    
    
        
    def find_all_translations(self):
        for trans_id in xrange(0, self.lattice.get_trans_count()):
            for repton_id in xrange(0, self.particles.number):
                rate = 1
                for rule in self.rules:
                    rate  = rate *  rule.get_rate(repton_id, trans_id)
                    if rate == 0:
                        break
                idx = self._get_coordinate(trans_id, repton_id)
                self.motion_matrix[idx] = self.motion_matrix[idx] * rate
                        
        #zapamietaj sume kumulacyjna dla drabinki
        self.cumulative_prob = self.motion_matrix.cumsum()
        
        
  
    
    def _get_coordinate(self, trans_id, repton_id):
        return trans_id * self.particles.number + repton_id
    
    
    
        
#if __name__ == "__main__":
    
    #epsilon = 0.1
    
    #symulator = BendingDynamics(reptons=6, link_length=1, dim=2, epsilon=epsilon, hernia=0.5, crossing=0.3, kappa=0.5)
    #print symulator.polimer.positions
    #print symulator.motion_matrix.reshape(8,6)
    
    
    
    #plik = open("traj.pos",'w')
    
    #for i in range(100000):
        #symulator.reconfigure()
        #nap = "%d" % i
        
        #for x,y in symulator.polimer.positions:
            #nap = "%s %d %d 0 " % (nap, x,y)
        #nap = "%s\n" % nap
        
        #plik.write(nap)
    #plik.close()
        
