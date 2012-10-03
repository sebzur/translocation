import numpy
import sys
sys.path.append('/home/kosmo/Git/translocation')
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
            if numpy.sqrt(((self.particles.positions[repton_id-1] - (self.particles.positions[repton_id]+t_vect)) ** 2).sum()) > length:
                return 0
                
        if (repton_id < self.particles.number - 1):
            length = self.particles.link_length[repton_id]
            if numpy.sqrt(((self.particles.positions[repton_id+1] - (self.particles.positions[repton_id]+t_vect)) ** 2).sum()) > length:
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



class Bending(base.Rule):
    def initialize(self, *args, **kwargs):
        self.kappa = kwargs.get('kappa')
        
    def get_update_list(self, repton_id, trans_id):
        #tutaj to bedzie dynamiczne - dwa sasiednie zawsze  potem wszystskie ad do kolejengo z innej komorki
        tab = [repton_id]
        
        if repton_id == 0:
            next_r = self.next_id(repton_id + 1)
            if not next_r is None:
                tab = tab + range(repton_id + 1, next_r+1)
            else:
                tab = tab + range(repton_id + 1, self.particles.number)
            return tab
        
        if repton_id == self.particles.number - 1:
            tab.append(repton_id)
            prev_r = self.prev_id(repton_id - 1)
            if not prev_r is None:
                tab = tab + range(prev_r, repton_id)
            else:
                tab = tab + range(0, repton_id)
            return tab
        
        
        
        prev_r = self.prev_id(repton_id - 1)
        if not prev_r is None:
            tab = range(prev_r, repton_id, 1) + tab
        else:
            tab = range(0, repton_id, 1) + tab

        
        next_r = self.next_id(repton_id + 1)
        if not next_r is None:
            tab = tab + range(repton_id + 1, next_r+1)
        else:
            tab = tab + range(repton_id + 1, self.particles.number)
        return tab
            
        return []
        
    def _get_inter_energy(self,vectors ):
        energy = 0
        for i in range(0,3):
            #slack-link daje 0
            if (vectors[i][0]==0 and vectors[i][1]==0 ) or (vectors[i+1][0]==0 and vectors[i+1][1]==0 ):
                energy = energy
            else:
                skalar = -1 * vectors[i][0]*vectors[i+1][0] + -1.*vectors[i][1]*vectors[i+1][1]
                energy = energy + 1 + skalar # 1 + cos
                
        #Jak sa TYLKO !!! dwa srodkowe slackiem to wtedy kat jest katem pomiedzy dwoma zewnetrznymi
        if (vectors[1][0]==0 and vectors[1][1]==0 ) and (vectors[2][0]==0 and vectors[2][1]==0 ):
            if (vectors[0][0]!=0 or vectors[0][1]!=0 ) and (vectors[3][0]!=0 or vectors[3][1]!=0 ):
                skalar = -1 * vectors[0][0]*vectors[3][0] + -1*vectors[0][1]*vectors[3][1]
                energy = energy + 1 + skalar
        
        return energy
        
    def _get_end_energy(self, vectors):
        energy = 0
        if numpy.all(vectors[0]==0) or numpy.all(vectors[1]==0):
            return energy
        
        skalar = -1 * vectors[0][0]*vectors[1][0] + -1*vectors[0][1]*vectors[1][1]
        return 1 + skalar
            
            
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        #glowa
        if repton_id == 0:
            tab_old = numpy.zeros((3,2))
            tab_old[0] = self.particles.positions[repton_id]
            tab_old[1] = self.particles.positions[repton_id+1]
            next_r = self.next_id(repton_id+1)
            if not next_r is None:
                tab_old[2] = 1.*self.particles.positions[next_r]
            else:
                tab_old[2] = 1.*self.particles.positions[repton_id+1]
            
            vectors = numpy.diff(tab_old, axis=0)
            energy_old = self._get_end_energy(vectors)
            tab_old[0] = self.particles.positions[repton_id] + t_vect
            vectors = numpy.diff(tab_old, axis=0)
            energy_new = self._get_end_energy(vectors)
        
            return numpy.exp(-0.5*self.kappa*(energy_new - energy_old))
            
        #ogon
        if repton_id == self.particles.number-1:
            tab_old = numpy.zeros((3,2))
            tab_old[0] = self.particles.positions[repton_id]
            tab_old[1] = self.particles.positions[repton_id-1]
            prev_r = self.prev_id(repton_id-1)
            if not prev_r is None:
                tab_old[2] = 1.*self.particles.positions[prev_r]
            else:
                tab_old[2] = 1.*self.particles.positions[repton_id-1]
            
            vectors = numpy.diff(tab_old, axis=0)
            energy_old = self._get_end_energy(vectors)
            tab_old[0] = self.particles.positions[repton_id] + t_vect
            vectors = numpy.diff(tab_old, axis=0)
            energy_new = self._get_end_energy(vectors)
          
            return numpy.exp(-0.5*self.kappa*(energy_new - energy_old))
        
          
        #jesli nie hernia to nas nie interesuje
        if numpy.any( self.particles.positions[repton_id-1] != self.particles.positions[repton_id+1]):
            return 1
            
        tab_old = numpy.zeros((5,2))
        
        tab_old[2] = 1.*self.particles.positions[repton_id]
        tab_old[1] = 1.*self.particles.positions[repton_id-1]
        tab_old[3] = 1.*self.particles.positions[repton_id+1]
        
        next_r = self.next_id(repton_id+1)
        prev_r = self.prev_id(repton_id-1)
    
        if not next_r is None:
            tab_old[4] = 1.*self.particles.positions[next_r]
        else:
            tab_old[4] = 1.*self.particles.positions[repton_id+1]
        
        if not prev_r is None:
            tab_old[0] = 1.*self.particles.positions[prev_r]
        else:
            tab_old[0] = 1.*self.particles.positions[repton_id-1]
        
        vectors = numpy.diff(tab_old, axis=0)
        energy_old = self._get_inter_energy(vectors)
        tab_old[2] = tab_old[2] + t_vect
        vectors_new = numpy.diff(tab_old, axis=0)
        energy_new = self._get_inter_energy(vectors_new)
        
        return numpy.exp(-0.5*self.kappa*(energy_new - energy_old))
        
    
    def next_id(self, repton_id):
        if repton_id == self.particles.number -1:
            return None
        else:
            for i in xrange(repton_id+1, self.particles.number):
                if numpy.any( self.particles.positions[repton_id] !=  self.particles.positions[i] ):
                    return i
        return None
    
    
    def prev_id(self, repton_id):
        if repton_id == 0:
            return None
        else:
            for i in xrange(repton_id-1, -1,-1):
                if numpy.any( self.particles.positions[repton_id] != self.particles.positions[i]):
                    return i
        return None
        
class SlackElectrostatic(base.Rule):
    
    def initialize(self, *args, **kwargs):
        self.el = kwargs.get('el')
        
    def get_update_list(self, repton_id, trans_id):
        return self.particles.get_neighbours_idx(repton_id)
     
    def _slack_number(self, repton_id, position):
        number = 0
        idx = repton_id + 1
        while idx < self.particles.number:
           
            if numpy.any( position != self.particles.positions[idx]):
                break
            number = number + 1
            idx = idx +1 
        
        idx = repton_id - 1
        while idx >= 0:
            if numpy.any( position != self.particles.positions[idx]):
                break
            number = number + 1
            idx = idx -1
            
        return number
        
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
     
        #jesli nie konce i nie hernie to sie nie zmiania
        
        if repton_id == 0 or repton_id == self.particles.number - 1:
            old = self._slack_number(repton_id, self.particles.positions[repton_id])
            new = self._slack_number(repton_id, self.particles.positions[repton_id] + t_vect )
            return numpy.exp(-0.5*self.el*(new-old))
        
         #jesli nie hernia to nas nie interesuje
        if numpy.any( self.particles.positions[repton_id-1] != self.particles.positions[repton_id+1]):
            return 1
       
        old = self._slack_number(repton_id, self.particles.positions[repton_id])
        new = self._slack_number(repton_id, self.particles.positions[repton_id] + t_vect )
        return numpy.exp(-0.5*self.el*(new-old))
        

class Initializer(base.Dynamics):

    def initialize_particles(self, *args, **kwargs):
       
        trans_number =  self.lattice.get_initial_translations().shape[0]
        
        for repton_id, pos in enumerate(self.particles.positions[1:]):
            repton_id += 1
            idx = numpy.random.randint(trans_number )
            if numpy.random.rand() < 0.7:
                self.particles.positions[repton_id] = self.particles.positions[repton_id-1] + self.lattice.get_translation(idx)
            else:
                self.particles.positions[repton_id] = self.particles.positions[repton_id-1]


class ReptationModel(Initializer):
        
    lattice = SquareLattice()
    rules_classes = [NoTension, Hernia, HorizontalElectricField]
    particles_class = Polymer

class RouseModel(Initializer):

    lattice = SecondNearestLattice()
    rules_classes = [NoTension, Hernia, CrossingBarrier, HorizontalElectricField]
    particles_class = Polymer


class RealisticModel(Initializer):
        
    lattice = SecondNearestLattice()
    rules_classes = [NoTension, Hernia, CrossingBarrier, Bending, SlackElectrostatic, HorizontalElectricField]
    particles_class = Polymer
      
    

class ProbabilityTest(object):
    
    directory = "data"
    
    def __init__(self, symulator):
        self.symulator = symulator
        self.pos = []
        self.mat = []
        
    def save_data(self, number):
        file_pos = "%s/position_%s.dat" % (self.directory,number)
        file_mat = "%s/motion_%s.dat" % (self.directory, number)
        
        numpy.savetxt(file_pos, self.symulator.particles.positions)
        numpy.savetxt(file_mat, self.symulator.motion_matrix)
    
    def load_data(self, number):
        file_pos = "%s/position_%s.dat" % (self.directory,number)
        file_mat = "%s/motion_%s.dat" % (self.directory, number)
        
        self.pos = numpy.loadtxt(file_pos)
        self.mat = numpy.loadtxt(file_mat)
    
    def check_data(self):
        
        self.symulator.particles.positions = 1 * self.pos
        self.symulator.motion_matrix.fill(1)
        self.symulator.find_all_translations()
        return numpy.all(self.mat == self.symulator.motion_matrix)
        
        
        
        

    
if __name__ == "__main__":
    
    
    symulator = ReptationModel(particles=4, link_length=1, hernia=0, epsilon=0.01)
    print symulator.lattice.get_translations()
    print symulator.lattice.get_initial_translations()
    #plik = open("traj.pos",'w')
    #for step in range(0,10000):
        #tmp="%s" % step;
        #for i in symulator.particles.positions:
            #tmp = "%s %d %d 0" % (tmp, i[0],i[1])
        #plik.write("%s\n" % tmp)
        #symulator.reconfigure()
    
    
    #plik.close()
        
     
    

    
    
    
    
  
    
    
