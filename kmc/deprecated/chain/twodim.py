# -*- coding: utf-8 -*-
from base import BaseChain

class TwoDimChain(BaseChain):



    @classmethod
    def states_to_vec(cls, states):
        return map(lambda state: {'E': 1, 'W': -1, 'S': 0, 'N': 0, 'p': 1, 'o': 0}[state], states)

    def get_moves(self):
        return (self._get_endpoint_transition, self._get_middlepoint_transition, self._get_biased_transition, self._get_uni_transition, self._get_hernia_transition,
                self._get_barrier_crossing_transition)

    # ------------------------------
    # String translation methods
    # ------------------------------
    def _get_endpoint_transition(self):
        # Jeśli ostatni link jest 1 lub -1, to przejście na końcu musi zamienić go na
        transaltion = {'o': ['N','S','E','W'], 'N': ['o'], 'S': ['o'], 'E': ['o'], 'W':['o']}
        move_dict = {'No': 0, 'So': 0, 'Eo': 1, 'Wo': -1, 'oN': 0, 'oS': 0, 'oE': -1, 'oW': 1}
        for i in (0, 1):
            states = self.side(i)
            if states: # czasami nic nie ma po ktorejs ze stron...
                for translated in transaltion[states[-1]]:
                    transition = '%s%s' % (states[-1], translated)
                    if i == 0:
                        # po lewej stronie
                        tup = (translated, self.states[1:])
                        mv = ((0, move_dict[transition]),)
                    else:
                        tup = (self.states[:-1], translated)
                        mv = ((-1, -move_dict[transition]),)
                    #print self.states, '--->', '%s%s' % tup, 'E', 'E', mv
                    yield '%s%s' % tup, 'E', 'E', mv

    def _get_middlepoint_transition(self):
        repr_split = [(i, self.states[i:i+2]) for i in range(self.links_number - 1)] # range leci do -1 zawsze, stąd nie -2 a -1
        #
        #   0   1   2   3 4 
        # *---*---*---*/\*--*
        # 0   1   2   3  4  5 
        #
        move_dict = {'Eo': -1,
                     'oE': +1,
                     'Wo': +1,
                     'oW': -1,
                     'oS': 0,
                     'So': 0,
                     'No': 0,
                     'oN': 0,
                     }
        for position, repr_frm in repr_split:
            if repr_frm in move_dict:
                #print self.states, '--->', '%s%s%s' % (self.states[:position], repr_frm[::-1], self.states[position+2:]), 'M', 'M', ((position + 1, move_dict[repr_frm]),)
                yield '%s%s%s' % (self.states[:position], repr_frm[::-1], self.states[position+2:]), 'M', 'M', ((position + 1, move_dict[repr_frm]),)

    def _get_barrier_crossing_transition(self):
        repr_split = [(i, self.states[i:i+2]) for i in range(self.links_number - 1)] # range leci do -1 zawsze, stąd nie -2 a -1
        #
        #   0   1   2   3 4 
        # *---*---*---*/\*--*
        # 0   1   2   3  4  5 
        #
        move_dict = {'EN': -1,
                     'ES': -1,
                     'NE': +1,
                     'SE': +1,
                     'WN': +1,
                     'WS': +1,
                     'NW': -1,
                     'SW': -1,
                     }
        for position, repr_frm in repr_split:
            if repr_frm in move_dict:
                #print self.states, '--->', '%s%s%s' % (self.states[:position], repr_frm[::-1], self.states[position+2:]), 'M', 'M', ((position + 1, move_dict[repr_frm]),)
                yield '%s%s%s' % (self.states[:position], repr_frm[::-1], self.states[position+2:]), 'C', 'C', ((position + 1, move_dict[repr_frm]),)

    def _get_hernia_transition(self):
        repr_split = [(i, self.states[i:i+2]) for i in range(self.links_number - 1)] # range leci do -1 zawsze, stąd nie -2 a -1
        #
        #   0   1   2   3 4 
        # *---*---*---*/\*--*
        # 0   1   2   3  4  5 
        #
        move_dict = {'oo': {'NS': 0, 'SN': 0, 'EW': 1, 'WE': -1},
                     'NS': {'oo': 0},
                     'SN': {'oo': 0},
                     'EW': {'oo': -1},
                     'WE': {'oo': 1},
                     }

        for position, repr_frm in repr_split:
            if repr_frm in move_dict:
                for n_dir in move_dict[repr_frm]:
#                    print self.states, '--->', '%s%s%s' % (self.states[:position], n_dir, self.states[position+2:]), 'H', 'H', ((position + 1, move_dict[repr_frm][n_dir]),)
                    yield '%s%s%s' % (self.states[:position], n_dir, self.states[position+2:]), 'H', 'H', ((position + 1, move_dict[repr_frm][n_dir]),)

    def _get_biased_transition(self):
        trans = {'po': ('B', 'F'),
                 'op': ('F', 'B')}
        move_dict = {'po': -1,
                     'op': +1}
        repr_split = [(i, self.states[i:i+2]) for i in range(self.links_number - 1) if self.states[i:i+2] in ('po', 'op') ]
        for position, repr_frm in repr_split:
            #print self.states, '---->', '%s%s%s' % (self.states[:position], repr_frm[::-1], self.states[position+2:]), trans[repr_frm][0], trans[repr_frm][1], ((position+1, move_dict[repr_frm]),)
            yield '%s%s%s' % (self.states[:position], repr_frm[::-1], self.states[position+2:]), trans[repr_frm][0], trans[repr_frm][1], ((position+1, move_dict[repr_frm]),)


    def _get_uni_transition(self):
        concat = self.states[0]+self.states[-1]
        move_dict = {'po': ((0, 1),(-1, 1)),
                     'op': ((0, -1),(-1, -1))}

        # To ewentulanie sprawdzić jeszcze
        trans = {'po': ('UF', 'UB'),
                 'op': ('UB', 'UF')}

        if concat in ('po', 'op'):
            #print self.states, '--->', '%s%s%s' % (concat[-1], self.states[1:-1], concat[0]), 'U', 'U', move_dict[concat]
            yield '%s%s%s' % (concat[-1], self.states[1:-1], concat[0]), trans[concat][0], trans[concat][1], move_dict[concat]
