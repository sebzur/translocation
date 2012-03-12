# -*- coding: utf-8 -*-
import sys
import numpy

sys.path.append('/magazyn/SEBZUR/bazaar/KMC/dev')
from kmc import base


class Chain(base.Configuration):
    # -------------------------------------
    # KMC handlers: Validators
    # ------------------------------------

    def __init__(self, *args, **kwargs):
        self.length = len(args[0])
        super(Chain, self).__init__(*args, **kwargs)
    
    def get_validators(self):
        #return (self.validator_wall_cross, self.validator_contractibility)
        return (self.validator_wall_cross,)

    def validator_wall_cross(self, cfg, **kwargs):
        for i in (0, 1):
            # Aby utowrzuć obiekt w ogóle
            if numpy.any(numpy.cumsum(self.transform_cfg_to_vec(self.get_cfg_side(i, cfg))) < 0):
                message = 'The state %s can not be created!' % cfg
                raise base.ValidationError(message)

    def validator_contractibility(self, cfg, **kwargs):
        # N - liczba slacków, na które nie pozwalamy
        # Przykładowo gdy N = 3 to nie pozwalamy na trzy i więcej kolejnych
        all_zero = 'o' * D
        for i in range(0, len(states) - D):
            if states[i:i+D] == all_zero:
                message = 'The state %s can not be created!' % states
                raise ValueError(message)

    def get_links_number(self):
        return self.length

    def get_length(self):
        return sum(self.states_to_vec())


    def get_distance_from_wall(self, side):
        """ Returns the distance of the last link from wall """
        return sum(self.states_to_vec(self.get_side(side, self.get_cfg())))


    def get_cfg_side(self, side, cfg):
        """ Returns the chain subset: 0 - left side, 1 - right side of the wall """
        cfg = cfg.split('p')[side]
        # To get the proper order, if user ask for left side (side=0)
        # we have to revert the chain configuration
        return cfg if side else cfg[::-1]
        
    def get_side(self, side):
        return self.get_cfg_side(side, self.get_cfg())

    # ---------------------------------------------------------------
    # Abstract methods below - Chain sublcasses must implement them
    # --------------------------------------------------------------

    def transform_cfg_to_vec(self, cfg):
        """ Returns vector representation of states """
        r = map(lambda state: self.get_state_to_vec_dict().get(state), cfg)
        return r

    def states_to_vec(self):
        """ Returns vector representation of states """
        return self.transform_cfg_to_vec(self.get_cfg())

    def get_state_to_vec_dict(self):
        raise NotImplementedError
