# -*- coding: utf-8 -*-
from base import Chain



class OneDimChain(Chain):
    RANGE = 2

    def get_state_to_vec_dict(self):
        return {'+': 1, '-': -1, 'o': 0, 'p': 1}

    def get_rules(self):
        #return (self.rule_endpoint, self.rule_middlepoint, self.rule_hernia, self.rule_biased)
        return (self.rule_endpoint,)

    # ------------------------------
    # String translation methods
    # ------------------------------

    def _rule_endpoint(self, connection):
        yield self.get_cfg(), 'E', 1

    def rule_endpoint(self, connection):
        # Jeśli ostatni link jest 1 lub -1, to przejście na końcu musi zamienić go na
        transaltion = {'o': ['+','-'], '+': ['o'], '-': ['o'], 'p': []}
        left = transaltion[self.get_cfg()[0]]
        right = transaltion[self.get_cfg()[-1]]
        yield self.get_cfg(), 'E', 0



    def _rule_endpoint(self, connection):
        # Jeśli ostatni link jest 1 lub -1, to przejście na końcu musi zamienić go na
        transaltion = {'o': ['+','-'], '+': ['o'], '-': ['o']}
        for i in (0, 1):
            #states = self._get_states_side(i)
            states = self.get_side(i)
            if states: # czasami nic nie ma po ktorejs ze stron...
                for translated in transaltion[states[-1]]:
                    transition = '%s%s' % (states[-1], translated)
                    if i == 0:
                        # po lewej stronie
                        tup = (translated, self.get_cfg()[1:])
                        #mv = ((0, move_dict[transition]),)
                        mv = 0
                    else:
                        tup = (self.get_cfg()[:-1], translated)
                        #mv = ((-1, -move_dict[transition]),)
                        mv = self.get_links_number()
                    yield '%s%s' % tup, 'E', (mv,)


    def rule_middlepoint(self, connection):
        anal_from = 0
        anal_to = self.get_links_number()


        if connection :
            anal_from = connection.pos[0] - self.RANGE if connection.pos[0] > self.RANGE -1 else 0
            anal_to = connection.pos[-1] + self.RANGE if connection.pos[-1] < self.get_links_number() - self.RANGE  else self.get_links_number()
            

        to_anal = self.get_cfg()[anal_from:anal_to]
        #repr_split = [(i, self.get_cfg()[i:i+2]) for i in range(self.get_links_number() - 1)] # range leci do -1 zawsze, stąd nie -2 a -1
        repr_split = [(i+anal_from, to_anal[i:i+2]) for i in range(len(to_anal)- 1)] # range leci do -1 zawsze, stąd nie -2 a -1

        #
        #   0   1   2   3 4 
        # *---*---*---*/\*--*
        # 0   1   2   3  4  5 
        #
        move_dict = {'+o': -1,
                     'o+': +1,
                     '-o': +1,
                     'o-': -1,
                     }
        for position, repr_frm in repr_split:
            if repr_frm in move_dict:
                yield '%s%s%s' % (self.get_cfg()[:position], repr_frm[::-1], self.get_cfg()[position+2:]), 'M', (position, position +1)


    def rule_hernia(self, connection):
        repr_split = [(i, self.get_cfg()[i:i+2]) for i in range(self.get_links_number() - 1)] # range leci do -1 zawsze, stąd nie -2 a -1
        #
        #   0   1   2   3 4 
        # *---*---*---*/\*--*
        # 0   1   2   3  4  5 
        #
        move_dict = {'oo': {'+-': 1, '-+': -1},
                     '+-': {'oo': -1},
                     '-+': {'oo': 1},
                     }

        for position, repr_frm in repr_split:
            if repr_frm in move_dict:
                for n_dir in move_dict[repr_frm]:
#                    print self.states, '--->', '%s%s%s' % (self.states[:position], n_dir, self.states[position+2:]), 'H', 'H', ((position + 1, move_dict[repr_frm][n_dir]),)
                    yield '%s%s%s' % (self.get_cfg()[:position], n_dir, self.get_cfg()[position+2:]), 'H', (position, position + 1)


    def rule_biased(self, connection):
        trans = {'po': ('B', 'F'),
                 'op': ('F', 'B')}
        move_dict = {'po': -1,
                     'op': +1}
        repr_split = [(i, self.get_cfg()[i:i+2]) for i in range(self.get_links_number() - 1) if self.get_cfg()[i:i+2] in ('po', 'op') ]
        for position, repr_frm in repr_split:
            #print self.states, '---->', '%s%s%s' % (self.states[:position], repr_frm[::-1], self.states[position+2:]), trans[repr_frm][0], trans[repr_frm][1], ((position+1, move_dict[repr_frm]),)
            yield '%s%s%s' % (self.get_cfg()[:position], repr_frm[::-1], self.get_cfg()[position+2:]), trans[repr_frm][0], (position, position + 1)

    def rule_sisters(self, connection):
        concat = self.get_cfg()[0] + self.get_cfg()[-1]

        move_dict = {'po': ((0, 1),),
                     'op': ((0, -1),)}

        # To ewentulanie sprawdzić jeszcze
        trans = {'po': ('UF', 'UB'),
                 'op': ('UB', 'UF')}
        #print 'Check', self.states, concat
        if concat in ('po', 'op'):
            yield self.get_cfg()[::-1], trans[concat][0], trans[concat][1], move_dict[concat], range(self.get_links_number() + 1)


if __name__ == "__main__":
    z = OneDimChain('+p+o' + 'o' * 300)
    for i in range(10000):
        if not i%100:
            print i
        z.reconfigure({'E': 1, 'M': 1, 'H': 0.5, 'B': 0.5, 'F': 2.0})
                       
