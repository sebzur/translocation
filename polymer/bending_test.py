
class Bending(Rule):
    def initialize(self, *args, **kwargs):
        self.rate = kwargs.get('hernia')
        self.kappa = kwargs.get("kappa")
        self.hard = numpy.exp(-4*self.kappa)
        self.easy = 1./self.hard
        
    
    
    def _get_end_energy(self, pos1, pos2, pos3):
        
        if numpy.all( pos1 == pos3) and numpy.any( pos1 != pos2):
            return 1
        
        if numpy.all(pos1 == pos2):
            return -1
        
        #90 stopni
        if numpy.all(pos1 != pos3):
            return 0
        
        #to nie prawda - liczy sie kontur jesli np. 2i 3 sa w jednej komorce
        #liczymy il ejest "kompresowanych poczawszy od 2.
        if numpy.any(pos1 == pos3):
            return -1
            
        
    def get_rate(self, repton_id, trans_id, *args, **kwargs):
        t_vect = self.lattice.get_translation(trans_id)
        
        #pierwszy i ostatni - inna zmiana energii
        if repton_id == 0 or repton_id == self.polimer.reptons - 1:
            pos_r = self.polimer.positions[repton_id]
            if repton_id == 0:
                pos_i= self.polimer.positions[repton_id+1]
                #sprawdz ile w komorce
                k=2
                while repton_id+k < self.polimer.reptons and numpy.all(self.polimer.positions[repton_id+1] == self.polimer.positions[repton_id+k]):
                    k = k+1
                pos_ii = self.polimer.positions[repton_id + k]
                
                
            elif repton_id == self.polimer.reptons - 1:
                pos_i= self.polimer.positions[repton_id-1]
                k=2
                while repton_id-k >= 0 and numpy.all(self.polimer.positions[repton_id-1] == self.polimer.positions[repton_id-k] ):
                    k = k-1
                pos_ii = self.polimer.positions[repton_id - k]
               
            old_e = self._get_end_energy(pos_r, pos_i, pos_ii)
            new_e = self._get_end_energy(pos_r+t_vect, pos_i, pos_ii)
            
            delta = new_e - old_e
            return numpy.exp(self.kappa* (-1* delta))
    
            
            
            
                
        ##srodkowy moze sie ruszyc !!!! 
        if numpy.all(self.polimer.positions[repton_id -1] == self.polimer.positions[repton_id]) and numpy.all(self.polimer.positions[repton_id] == self.polimer.positions[repton_id+1]):
            return self.rate * self.hard
        
        
        #srodkowy moze wskoczyc miedzy dwa 
        
        if numpy.all(self.polimer.positions[repton_id - 1] == self.polimer.positions[repton_id+1]) and numpy.all( (self.polimer.positions[repton_id]+t_vect) == self.polimer.positions[repton_id+1]):
            return self.rate * self.easy
        return 1
