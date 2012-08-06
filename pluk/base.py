import numpy


class Polimer(object):
    """Polimer """
    def __init__(self, reptons, link_length, dim, *args, **kwargs):
        self.dim = dim
        self.reptons = reptons
        link_number = reptons - 1
        
        self.positions = numpy.zeros((reptons, dim))
        self.link_length = numpy.zeros(link_number)
        self.link_length.fill(link_length)
       
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
    
    
    def get_initial_translations(self):
        """ sometimes some transletions can't be used to create polimer - [-1,1]"""
        return self.get_translations()
    
    def get_trans_count(self):
        return self._get_trans_count
        #return self.get_translations().shape[0]
        
    def get_translation(self, idx):
        return self.get_translations()[idx]

        
class SquareLattice(Translation):
    """Square lattice"""
    vectors = numpy.array( [[0, 1], [1, 0], [0, -1], [-1, 0] ] )
    
    def get_translations(self):
        return self.vectors


class SecondNearestLattice(Translation):
    vectors = numpy.array( [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, -1], [-1, 1]  ] )
    
    def get_translations(self):
        return self.vectors

    def get_initial_translations(self):
        return self.vectors[:4]
    
    
class Rule(object):
    """ Base class"""
    def __init__(self, polimer, lattice , *args, **kwargs):
        self.polimer = polimer
        self.lattice = lattice
        self.rate = 1
        self.initialize(*args, **kwargs)
        
        

    def initialize(self, *args, **kwargs):
        pass
    
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        raise NotImplementedError
   
        

class NoTension(Rule):
    """Link can't be broken"""
    
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        if ( repton_id ) > 0:
            #znajdz dlugosc z lewej strony 
            #oldeglosc 0-1 - length[0], 1-2- length[1] ...
            length = self.polimer.link_length[repton_id-1]
            if ((self.polimer.positions[repton_id-1] - (self.polimer.positions[repton_id]+t_vect)) ** 2).sum() > length:
                return 0
                
        if (repton_id < self.polimer.reptons - 1):
            length = self.polimer.link_length[repton_id]
            if ((self.polimer.positions[repton_id+1] - (self.polimer.positions[repton_id]+t_vect)) ** 2).sum() > length:
                return 0
       
        return self.rate
    

#To juz chyba niepotrzebne
#class NoHernia(Rule):
    #""" Hernias are not allowed"""
    #def get_rate(self, repton_id, trans_id, *args, **kwargs):
        #"""Zakladam, ze jezeli ruch ni ejst hernia to zwracam rate = 1 - multiplikatywnosc"""
        #t_vect = self.lattice.get_translation(trans_id)
        
        #if repton_id == 0 or repton_id == self.polimer.reptons - 1:
            #return 1
        
        ##srodkowy nie moze sie ruszyc !!!! - anihilacja
        #if numpy.all(self.polimer.positions[repton_id -1] == self.polimer.positions[repton_id]) and numpy.all(self.polimer.positions[repton_id] == self.polimer.positions[repton_id+1]):
            #return 0
            
        ##srodkowy nie moze wskoczyc miedzy dwa - kreacja
        #if numpy.all(self.polimer.positions[repton_id - 1] == self.polimer.positions[repton_id+1]) and numpy.all( (self.polimer.positions[repton_id]+t_vect) == self.polimer.positions[repton_id+1]):
            #return 0
            
        #return 1
        

class Hernia(Rule):
    """ Hernias are allowed"""
    def initialize(self, *args, **kwargs):
        self.rate = kwargs.get('hernia')
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        #pierwszy i ostatni nie tworzy herni - zwraca 1 - multiplikatywnosc
        if repton_id == 0 or repton_id == self.polimer.reptons - 1:
            return 1
        
                
        ##srodkowy moze sie ruszyc !!!! 
        if numpy.all(self.polimer.positions[repton_id -1] == self.polimer.positions[repton_id]) and numpy.all(self.polimer.positions[repton_id] == self.polimer.positions[repton_id+1]):
            return self.rate
        
        
        #srodkowy moze wskoczyc miedzy dwa 
        
        if numpy.all(self.polimer.positions[repton_id - 1] == self.polimer.positions[repton_id+1]) and numpy.all( (self.polimer.positions[repton_id]+t_vect) == self.polimer.positions[repton_id+1]):
            return self.rate
        return 1
            
class HorizontalElectricField(Rule):
    
    def initialize(self,*args, **kwargs):
        self.B = numpy.exp(0.5*kwargs.get('epsilon'))
        self._B = 1.0/self.B
        
    def get_rate(self,repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        if t_vect[0] == 1:
            return self.B
        if t_vect[0] == -1:
            return self._B
        return 1

class CrossingBarrier(Rule):
    """ Hernias are allowed"""
    def initialize(self, *args, **kwargs):
        self.rate = kwargs.get('crossing')
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        #po pierwsze - jesli nie po skosie to nie barier crossing
        if t_vect[0] == 0 or t_vect[1] == 0:
            return 1
        
        # jesli reptony sasiedne w jednej komorce  to nie (hernie nie ma CB  musz byc dwie hernie)
        if repton_id != 0 and repton_id != self.polimer.reptons-1:
            if numpy.all(self.polimer.positions[repton_id -1] == self.polimer.positions[repton_id+1]):
                return 0
        
        #odleglos sprawdzil wczesniej - wiec ok
        return self.rate
        
        
class HorizontalElectricField(Rule):
    """ Apply horizontal electric field"""
    def initialize(self, *args, **kwargs):
        self.rate = numpy.exp(0.5*kwargs.get('epsilon'))
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        if t_vect[0] == 1:
            return self.rate
        else:
            return 1./self.rate
            
        return 1


class Dynamics(object):
    """Dynamics - base class"""
    lattice = None
    rules_classes = []
    
    def __init__(self, *args, **kwargs):
        
        self.kwargs = kwargs
        self.args = args
        
        reptons = kwargs.get('reptons')
        link_length = kwargs.get('link_length')
        dim = kwargs.get('dim')
        
        self.rules = []
        self.polimer = Polimer(reptons, link_length, dim)
        self.initialize_rules(*args, **kwargs)
        self.initialize_polimer(*args, **kwargs)
        
        self.motion_matrix = numpy.zeros(reptons * self.lattice.get_trans_count())
        self.cumulative_prob = self.motion_matrix.cumsum()
        self.find_translations()
        
    def initialize_rules(self, *args, **kwargs):
        for idx, rule in enumerate(self.rules_classes):
            self.rules.append(rule(self.polimer, self.lattice, *args, **kwargs))
   
   
    def initialize_polimer(self, *args, **kwargs):
        
        trans_number =  self.lattice.get_initial_translations().shape[0]
        
        for repton_id, pos in enumerate(self.polimer.positions[1:]):
            repton_id += 1
            idx = numpy.random.randint(trans_number )
            if numpy.random.rand() < 0.7:
                self.polimer.positions[repton_id] = self.polimer.positions[repton_id-1] + self.lattice.get_translation(idx)
            else:
                self.polimer.positions[repton_id] = self.polimer.positions[repton_id-1]
            

    
    
    def get_lifetime(self, *args, **kwargs):
        cum_prob = self.cumulative_prob[-1]
        random = numpy.random.uniform(low=0.0000000001, high=1)
        return -1.0*numpy.log(random)/cum_prob
    
        
    def reconfigure(self, *args, **kwargs):
       # rand_nr = numpy.random.uniform(0, self.cumulative_prob[-1])
        rand_nr = numpy.random.rand() * self.cumulative_prob[-1]
       
        for idx, prob in enumerate(self.cumulative_prob):
            if rand_nr <= prob:
                trans_id, repton_id = divmod(idx, self.polimer.reptons)
                t_vect = self.lattice.get_translation(trans_id) 
                
                break
                
        self.polimer.positions[repton_id] += t_vect
        self.update(repton_id)
        
        
    def update(self, repton_id):
        
        #wywal te co nie sa dozwolone z macierzy dozwolonych ruchow
        for trans_id in xrange(0, self.lattice.get_trans_count()):
            idx = self._get_coordinate(trans_id, repton_id)
            self.motion_matrix[idx] = 0
        
            if repton_id > 0:
                idx = self._get_coordinate(trans_id, repton_id-1)
                self.motion_matrix[idx] = 0
                
            if repton_id < self.polimer.reptons - 1:
                idx = self._get_coordinate(trans_id, repton_id+1)
                self.motion_matrix[idx] = 0
        
        #update
        if repton_id == 0:
            tab = [0, 1]
        elif repton_id == self.polimer.reptons - 1:
            tab = [repton_id-1, repton_id]
        else:   
            tab = [repton_id-1, repton_id, repton_id+1]
        
        for trans_id in xrange(0, self.lattice.get_trans_count()):
            for repton in tab:
                rate = self._get_rate(repton, trans_id)
                idx = self._get_coordinate(trans_id, repton)
                self.motion_matrix[idx] = rate
        
        self.cumulative_prob = self.motion_matrix.cumsum()
    
        
    def find_translations(self):
        for trans_id in xrange(0, self.lattice.get_trans_count()):
            for repton_id in xrange(0, self.polimer.reptons):
                rate  =  self._get_rate(repton_id, trans_id)
                if rate  != 0:
                    idx = self._get_coordinate(trans_id, repton_id)
                    self.motion_matrix[idx] = rate
                    
        #zapamietaj sume kumulacyjna dla drabinki
        self.cumulative_prob = self.motion_matrix.cumsum()
        
        
    def _get_rate(self, repton_id, trans_id):
        rate = 1
        for rule in self.rules:
            rate *= rule.get_rate(repton_id, trans_id)
            if rate == 0:
                return 0
        return rate
    
    def _get_coordinate(self, trans_id, repton_id):
        return trans_id * self.polimer.reptons + repton_id
    
    
    
class TestDynamics(Dynamics):
    """Electroforesis"""
    lattice = SecondNearestLattice()
    rules_classes = [NoTension, Hernia, CrossingBarrier, HorizontalElectricField]
    
    
        
if __name__ == "__main__":
    
    epsilon = 0.1
    
    symulator = TestDynamics(reptons=10, link_length=1, dim=2, epsilon=epsilon, hernia=0.5, crossing=0.3)
    plik = open("traj.pos",'w')
    
    for i in range(10000):
        symulator.reconfigure()
        nap = "%d" % i
        
        for x,y in symulator.polimer.positions:
            nap = "%s %d %d 0 " % (nap, x,y)
        nap = "%s\n" % nap
        
        plik.write(nap)
    plik.close()
        
