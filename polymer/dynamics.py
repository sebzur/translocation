import numpy
from pluk import base

class Polymer(base.Particles):
    
    def __init__(self, reptons, dim, *args, **kwargs):
        super(Polymer, self).__init__(reptons, dim, *args, **kwargs)
        link_number = reptons - 1
        self.link_length = numpy.zeros(link_number)
        link_length = kwargs.get('link_length', 1)
        self.link_length.fill(link_length)
    
    
class SquareLattice(base.Translation):
    """Square lattice"""
    vectors = numpy.array( [[0, 1], [1, 0], [0, -1], [-1, 0] ] )
    
    def get_translations(self):
        return self.vectors


class SecondNearestLattice(base.Translation):
    vectors = numpy.array( [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, -1], [-1, 1]  ] )
    
    def get_translations(self):
        return self.vectors

    def get_initial_translations(self):
        return self.vectors[:4]
        

        

class NoTension(base.Rule):
    """Constructor gets always particles objects, lattice, args and kwargs"""
    def get_update_list(self, repton_id, trans_id):
        return self.particles.get_neighbours_idx(repton_id)
    
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        if ( repton_id ) > 0:
            #znajdz dlugosc z lewej strony 
            #oldeglosc 0-1 - length[0], 1-2- length[1] ...
            length = self.particles.link_length[repton_id-1]
            if ((self.particles.positions[repton_id-1] - (self.particles.positions[repton_id]+t_vect)) ** 2).sum() > length:
                return 0
                
        if (repton_id < self.particles.number - 1):
            length = self.particles.link_length[repton_id]
            if ((self.particles.positions[repton_id+1] - (self.particles.positions[repton_id]+t_vect)) ** 2).sum() > length:
                return 0
       
        return self.rate

class Hernia(base.Rule):
    """ Hernias are allowed"""
    def initialize(self, *args, **kwargs):
        self.rate = kwargs.get('hernia')
    
    def get_update_list(self, repton_id, trans_id):
        return self.particles.get_neighbours_idx(repton_id)
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        #pierwszy i ostatni nie tworzy herni - zwraca 1 - multiplikatywnosc
        if repton_id == 0 or repton_id == self.particles.number - 1:
            return 1
        
        ##srodkowy moze sie ruszyc !!!! 
        if numpy.all(self.particles.positions[repton_id -1] == self.particles.positions[repton_id]) and numpy.all(self.particles.positions[repton_id] == self.particles.positions[repton_id+1]):
            return self.rate
        
        #srodkowy moze wskoczyc miedzy dwa 
        if numpy.all(self.particles.positions[repton_id - 1] == self.particles.positions[repton_id+1]) and numpy.all( (self.particles.positions[repton_id]+t_vect) == self.particles.positions[repton_id+1]):
            return self.rate
   
        return 1

class CrossingBarrier(base.Rule):
    """ Hernias are allowed"""
    def initialize(self, *args, **kwargs):
        self.rate = kwargs.get('crossing')
        
    def get_update_list(self, repton_id, trans_id):
        return self.particles.get_neighbours_idx(repton_id)
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        #po pierwsze - jesli nie po skosie to nie barier crossing
        if t_vect[0] == 0 or t_vect[1] == 0:
            return 1
        
        # jesli reptony sasiedne w jednej komorce  to nie (hernie nie ma CB  musz byc dwie hernie)
        if repton_id != 0 and repton_id != self.particles.number-1:
            if numpy.all(self.particles.positions[repton_id -1] == self.particles.positions[repton_id+1]):
                return 0
        
        #odleglos sprawdzil wczesniej - wiec ok
        return self.rate
        
        
class HorizontalElectricField(base.Rule):
    """ Apply horizontal electric field"""
    def initialize(self, *args, **kwargs):
        self.rate = numpy.exp(0.5*kwargs.get('epsilon'))
        
    def get_update_list(self, repton_id, trans_id):
        return []
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        if t_vect[0] == 1:
            return self.rate
        elif t_vect[0] == -1:
            return 1./self.rate
        return 1

        
        
        

class PolymerDynamics(base.Dynamics):
        
    lattice = SquareLattice()
    rules_classes = [NoTension, Hernia, CrossingBarrier, HorizontalElectricField]
    particles_class = Polymer
        
        
    def initialize_particles(self, *args, **kwargs):
       
        trans_number =  self.lattice.get_initial_translations().shape[0]
        
        for repton_id, pos in enumerate(self.particles.positions[1:]):
            repton_id += 1
            idx = numpy.random.randint(trans_number )
            if numpy.random.rand() < 0.7:
                self.particles.positions[repton_id] = self.particles.positions[repton_id-1] + self.lattice.get_translation(idx)
            else:
                self.particles.positions[repton_id] = self.particles.positions[repton_id-1]
    
    
    
    
if __name__ == "__main__":
    
    
    symulator = PolymerDynamics(particles=10, link_length=1, hernia=0.5, crossing=0.2, epsilon=1)
    for i in xrange(1000):
        symulator.reconfigure()
    
    
