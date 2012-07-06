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


    def _randomize_reptons(self):
        """ Randomizes repton positions """
        for position in range(1, self.positions.shape[0]):
            trans = self.dynamics.select_translation(prev_trans=None)
            t_vect = self.dynamics.translations.get(trans)
            self.positions[position] = self.positions[position-1] + t_vect


    def run(self, steps):
        repton_id = numpy.random.randint(0, self.positions.shape[0])
        print 'ciagnie', repton_id

        trans = self.dynamics.select_translation(prev_trans=None)
        t_vect = self.dynamics.translations.get(trans)
      
        old_pos = self.positions[repton_id]

        self.positions[repton_id] += t_vect


        for step in (-1, 1):
            base_id = repton_id
            position_id = repton_id + step

            while position_id >= 0 and position_id <= self.positions.shape[0]:
                if ((self.positions[base_id] - self.positions[position_id]) ** 2).sum() <= 1:

                    tt = old_pos - self.positions[position_id]
                    old_pos = self.positions[position_id]

                    self.positions[position_id] += tt
                    base_id = position_id
                    position_id += step
                else:
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
    for x, y in p.positions:
        print x, "\t", y
    p.run(1)
    for x, y in p.positions:
        print x, "\t", y
    
    
