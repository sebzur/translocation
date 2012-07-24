import numpy

class Polymer(object):
    def __init__(self, dynamics_class, link_length, reptons,  *args, **kwargs):
        """ Initialize polymer object. 
        
        Arguments:
        - dynamics_class: represents polymer dynamics
        - link_length: the maxmimum repton to repton distance
        - reptons: how many reptons are there in the chain
        """

        self.dynamics = dynamics_class(link_length)
        # Reptons are represented as points in 
        # space, each repton is a row in the 
        # `self.reptons` matrix
        self.positions = numpy.zeros((reptons, self.dynamics.get_dim()))
        # let's randomize the positions
        self._randomize_reptons()

    def get_reptons_number(self):
        return self.positions.shape[0]
        
    def prepare_translations(self):
        self.translations = {}
        
        for i in self.dynamics.translations.keys():
            self.translations[i]=[]
        
        for repton_id, val in enumerate(self.positions):
            for trans in self.dynamics.translations.keys():
                print trans
                #wez translacje
                t_vect = self.dynamics.translations.get(trans)
                if self.rule0_reptation(repton_id, t_vect):
                    self.translations[trans] += [repton_id]
        
    def update_translations(self, repton_id):
        #wywal te co nie sa dozwolone z ztablicy a dozwolone dodaj
        #PROBLEM Z PRZYPADKU OGRANICZONEJ OBJETOSCI !!!!
        pass
        
    def _randomize_reptons(self):
        """ Randomizes repton positions """
        for position in range(1, self.positions.shape[0]):
            while 1:  #wtf !!!!!!! - bo na rzie nie wiem jak 
                trans = self.dynamics.select_translation(prev_trans=None)
                t_vect = self.dynamics.translations.get(trans)
                if self.rule3_C(position, t_vect, 3, only_left=True):
                    break
                    
            self.positions[position] = self.positions[position-1] + t_vect

    #Nature rules as cost function
    #zwraca wektor cms
    def go_right(self, conf):
        return conf.sum(axis=0)/conf.shape[0]
        
    
    
    
    #end Nature
    #some specific rules for initial repton moves
    #f return True - move is allowed, in False - no allowed
    
    def rule0_reptation(self, repton_id, t_vect):
        #ostatni i pierwszy ida "normalnie"
        if repton_id == 0 or repton_id == self.get_reptons_number()-1:
            return self.rule1_lenth(repton_id, t_vect)
        
        #pozostale ida po konturze
        new_pos = self.positions[repton_id] + t_vect
        if numpy.all(new_pos == self.positions[repton_id-1]) or numpy.all(new_pos == self.positions[repton_id+1]):
            return self.rule1_lenth(repton_id, t_vect)
        
        return False
        
        
    def rule1_lenth(self,repton_id, t_vect):
        #left chain
        broken = False
        if ( repton_id ) > 0:
            if ((self.positions[repton_id-1] - (self.positions[repton_id]+t_vect)) ** 2).sum() > 1:
                broken = True
        #right chain 
        if not broken:
            if (repton_id < self.get_reptons_number() - 1):
                if ((self.positions[repton_id+1] - (self.positions[repton_id]+t_vect)) ** 2).sum() > 1:
                    broken = True
        return not broken
        
    def rule2_V(self, repton_id, t_vect, V):
        #apply rule in tmp
        test_conf = 1.0 * self.positions
        test_conf[repton_id] += t_vect
        #check how many identical points are there
        if len(filter( lambda x: numpy.all(x == test_conf[repton_id]), test_conf)) <= V:
            return True
        return False

    def rule3_C(self, repton_id, t_vect, C, only_left=False):
        #apply rule in tmp
        test_conf = 1.0 * self.positions
        test_conf[repton_id] += t_vect
        #check how many identical points are there
        
        #warunek zeby mozna bylo na poczatku
        if not only_left:
            c_tmp = len(filter( lambda x: numpy.all(x == test_conf[repton_id]), test_conf[repton_id:repton_id+C+1]))
        else:
            c_tmp=1;
            
        if repton_id >= C:
            c_tmp += len(filter( lambda x: numpy.all(x == test_conf[repton_id]), test_conf[repton_id-C:repton_id]))
        else:
            c_tmp += len(filter( lambda x: numpy.all(x == test_conf[repton_id]), test_conf[0:repton_id]))
            
        if c_tmp <= C: 
            return True
        
        return False
        
        
    def single_step(self,step_nr):
        
        old_cost = self.go_right( self.positions)
        
        repton_id = numpy.random.randint(0, self.positions.shape[0])
        trans = self.dynamics.select_translation(prev_trans=None)
        t_vect = self.dynamics.translations.get(trans)
        
        #allowed = self.rule0_reptation(repton_id, t_vect)
        allowed = self.rule1_lenth(repton_id, t_vect)
        #if allowed:
           #allowed = self.rule3_C(repton_id, t_vect, 3)
      
        #if allowed:
            #tmp_conf = self.positions + t_vect
            #new_cost = self.go_right(tmp_conf)
            #delta = new_cost - old_cost
            #if delta[1] < 1:
                #if numpy.random.ranf() > 0.5:
                    #allowed = False
                
        if allowed: 
            self.positions[repton_id] += t_vect
            return True
        else:
            #print step_nr
            return False
        
        

    def run(self, steps):
        self.prepare_translations()
        krok = 0
        plik = open('polimer_kontur_test.pos','w')
        #for step in range(0, steps):
        while(krok < steps):
            if self.single_step(krok):
                nap ="%d" % krok
                for i in self.positions:
                    x,y = i
                    nap = "%s %d %d 0" %(nap,x,y)
                plik.write("%s\n"%nap)
                krok += 1
                #    self.save_conf(step)
        return 
        
        #stare
        repton_id = numpy.random.randint(0, self.positions.shape[0])
        trans = self.dynamics.select_translation(prev_trans=None)
        t_vect = self.dynamics.translations.get(trans)
        
        start_pos = 1*self.positions[repton_id]
      
        self.positions[repton_id] += t_vect
        #print "poszedl na", self.positions[repton_id]
      
        for step in (-1, 1):
            old_pos = 1*start_pos
            base_id = repton_id
            position_id = repton_id + step
            
            while position_id >= 0 and position_id < self.positions.shape[0]:
                #print "wybrany ", position_id, " z ", self.positions[position_id]
                if ((self.positions[base_id] - self.positions[position_id]) ** 2).sum() > 1:
                    tt = old_pos - self.positions[position_id]
                    old_pos = 1*self.positions[position_id]
                    self.positions[position_id] += tt
                    #print "wybrany poszedl na  ",self.positions[position_id] 
                    base_id = position_id
                    position_id += step
                else:
                    #print "poszedl break"
                    break
                    

    
        

class Translation(object):
    """ A base class for all dynamics. """

    def __init__(self, link_length, *args, **kwargs):
        self.link_length = link_length
        self.translations = self.get_all_translations()

    def select_translation(self, prev_trans, *args, **kwargs):
        """ 

        Returns the translation name (a dict key) that will be choosen to 
        update the repton position.

        """
        
        # get all posible translation vectors, with respects
        # to the previous one (if provided, i.e. not none)
        current_translations = self.get_translations(prev_trans, *args, **kwargs)
        
        # now select the tranlaction to be applied
        cumulated_probs = numpy.array([self.get_rate(translation, *args, **kwargs) for translation in current_translations]).cumsum()
        rand_num = numpy.random.uniform(0, cumulated_probs[-1])
        for prob_value, connection in zip(cumulated_probs, current_translations):
            if rand_num <= prob_value:
                return connection

    def get_rate(self, translation, *args, **kwargs):
        return getattr(self, "rate_%s" % translation)(*args, **kwargs)

    def get_translations(self, prev_trans, *args, **kwargs):
        if prev_trans:
            self.get_conditional_translations(prev_trans, *args, **kwargs)
        return self.translations.keys()

    def get_dim(self):
        """ Returns the system dimensionality. This will be used
        to create the polymer representation array 

        """
        
        raise NotImplementedError

    def get_all_translations(self):
        """ Returns all possible tranlations, note, that this will define
        the latice also.

        """

        raise NotImplementedError


    def get_conditional_translations(self, prev_trans, *args, **kwargs):
        """ Returns possible translaction with respect to the previous
        one + some extra args 

        """
        
        raise NotImplementedError

class SquareTranslation(Translation):
    
    def get_all_translations(self):
        return {'up': numpy.array((0, 1)),
                'right': numpy.array((1, 0)),
                'down': numpy.array((0, -1)),
                'left': numpy.array((-1, 0))}


    def get_dim(self):
        return self.get_all_translations().get('up').size

    def rate_up(self, *args, **kwargs):
        return 0.25

    def rate_right(self, *args, **kwargs):
        return 0.25

    def rate_left(self, *args, **kwargs):
        return 0.25

    def rate_down(self, *args, **kwargs):
        return 0.25


class SquareReptation(SquareTranslation):
    def get_limited_translations(self, prev_trans, *args, **kwargs):
        return self.get_all_transitions()
        
    

if __name__ == "__main__":
    # Jus a test..
    p = Polymer(SquareReptation, 1.0, 10)
    p.run(20000)

  