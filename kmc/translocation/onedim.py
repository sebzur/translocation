# -*- coding: utf-8 -*-
from base import Chain, can_exist
from kmc import process, base
import numpy
import copy
import pickle
import os

VALID = {':+-': [':+o'],
         ':o+': [':+o', 'o:+'],
         '++:': ['o+:'],
         'o:o': ['o:+', '+:o'],
         'o+:': ['++:', '+o:', ':+o', '-+:'],
         'o:+': ['+:+', ':o+', 'o:o'],
         '-+:': ['o+:',],
         '+o:': ['o+:', '+:o'],
         '+:+': ['o:+', '+:o'],
         ':++': [':+o',],
         ':+o': [':++', ':o+', ':+-', 'o+:'],
         '+:o': ['+:+', 'o:o', '+o:'],
         }


class Updater(base.Connection):
    
    def __init__(self, rate, side, position, action, repton_id):
        self.rate = rate
        self.side = side
        self.position = position
        self.action = action
        self.repton_id = repton_id

    def get_rate(self):
        return self.rate

    def get_handled_repton(self):
        return self.repton_id

    def get_id(self):
        return "%s%d%+d" % (self.get_rate(), self.get_handled_repton(), self.action)

    def __call__(self, rpr, **kwargs):
       getattr(rpr, self.side)[self.position] += self.action

class BiasUpdater(base.Connection):
    
    def __init__(self, rate, repton_id):
        self.rate = rate
        self.repton_id = repton_id

    def __call__(self, cfg, **kwargs):
        rev = {'F': ('trans', 'cis'), 'B': ('cis', 'trans')}
        _new = numpy.zeros(getattr(cfg, rev[self.rate][0]).size + 1)
        _new[1:] += getattr(cfg, rev[self.rate][0])
        setattr(cfg, rev[self.rate][0], _new)
        setattr(cfg, rev[self.rate][1], getattr(cfg, rev[self.rate][1])[1:])

    def get_handled_repton(self):
        return self.repton_id

    def get_rate(self):
        return self.rate

    def get_action(self):
        if self.rate == 'F':
            return 1
        else:
            return -1

    def get_id(self):
        return "%s%d%+d" % (self.get_rate(), self.get_handled_repton(), self.get_action())


class JumpUpdater(base.Connection):
    
    def __init__(self, rate, repton_id):
        self.rate = rate
        self.repton_id = repton_id

    def __call__(self, rpr):
        tr = {'UF': ('trans', 'cis'), 'UB': ('cis', 'trans')}
        setattr(rpr, tr[self.rate][1], getattr(rpr, tr[self.rate][0]))
        setattr(rpr, tr[self.rate][0], numpy.array([]))

    def get_rate(self):
        return self.rate

    def get_handled_repton(self):
        return self.repton_id

    def get_action(self):
        if self.rate == 'UF':
            return 1
        else:
            return -1

    def get_id(self):
        return "%s%d%+d" % (self.get_rate(), self.get_handled_repton(), self.get_action())


class Representation(object):

    def __init__(self, cis, trans):
        self.cis = cis
        self.trans = trans
        self.length = self.cis.size + self.trans.size + 1

    def __str__(self):
        tr = {0: 'o', 1: '+', -1: '-'}
        _c = {'cis': '', 'trans': ''}
        for attr in ('cis', 'trans'):
            _side = numpy.copy(getattr(self, attr))
            _side[1:] = _side[1:] - _side[:-1]
            _c[attr] += ''.join(map(lambda x: tr[x], _side))
        return "%s:%s" % (_c['cis'][::-1], _c['trans'])

    def reptons_to_ranges(self, reptons):

        shifted = reptons - (self.cis.size + 2)
        trans = numpy.compress(shifted > -1, shifted).tolist()
        cis = (-(numpy.compress(shifted < -1, shifted) + 2)[::-1]).tolist()

        # uwaga na tolist - muszą być listy, żeby poniższe działąło
        # miałem błąd i 3 godziny szukałem

        if len(cis) and cis[-1] < self.cis.size:
            cis = cis + [cis[-1] + 1]

        if len(cis) and cis[0] > 0:
            cis = [cis[0] - 1] + cis

        if len(trans) and trans[-1] < self.trans.size:
            trans = trans + [trans[-1] + 1]

        if len(trans) and trans[0] > 0:
            trans = [trans[0] - 1] + trans

        cis = numpy.array(cis)
        trans = numpy.array(trans)

        # ------------------
#        if cis.size == 1 and cis[0] == 0:
#            cis = numpy.array([0, 1])
#        if trans.size == 1 and trans[0] == 0:
#            trans = numpy.array([0, 1])

#        if cis.size == 0 and trans[0] == 1:
#            trans = numpy.array([0] + trans.tolist())

#        if trans.size == 0 and cis[0] == 1:
#            cis = numpy.array([0] + cis.tolist())
        # ------------------

        return cis, trans

    def __eq__(self, other):
        return numpy.array_equal(self.cis, other.cis) and numpy.array_equal(self.trans, other.trans)


class OneDimChain(Chain):

    def get_rules(self):
        #return (self.rule_endpoint, self.rule_middlepoint, self.rule_biaspoint, self.rule_hernia, self.rule_switch)
        return (self.rule_endpoint, self.rule_biaspoint, self.rule_middlepoint, self.rule_hernia, self.rule_switch)

    # ------------------------------
    # String translation methods
    # ------------------------------

    def rule_endpoint(self, connection):
        cfg = self.get_cfg()
        mod = {1: [-1], 0: [1, -1], -1: [1]}
        rev = {'cis': 'trans', 'trans': 'cis'}
        rept = {'cis': 0, 'trans': cfg.cis.size + cfg.trans.size +1}

#        if connection:
#            if not  0 in self.get_connections().get_clear_range(connection):
#                rept.pop('cis')
#            if not cfg.cis.size + cfg.trans.size in self.get_connections().get_clear_range(connection):
#                rept.pop('trans')
            
 
        for attr in rept.keys():            
            # możę nie być nic w cis/trans 
            if not getattr(cfg, attr).size:
                continue

            # diff can be one of:
            # 0: slack; 1: taut +, -1 taut -
            diff = getattr(cfg, attr)[-1] - getattr(cfg, attr)[-2] if getattr(cfg, attr).size > 1 else getattr(cfg, attr)[-1]
            for change in mod[diff]:
                # jeżeli odległość ostatniego od ściany jest 0 i będziemy próbowali
                # zmienić na -1 to nie możemy tego zrobić
                if getattr(cfg, attr)[-1] == 0 and change == -1:
                    continue

                # jeżeli jest akumulacja reptonów, też nie możemy
                tst = getattr(cfg, attr).copy()
                tst[-1] += change
                if not self.can_exist(tst, tst.size-1, self.C_LIMIT):
                    continue

                yield Updater('E', attr, -1, change, rept[attr])


    def get_update(self, connection):
        cfg = self.get_cfg()

#        print 'Przetwarza', cfg

        if connection:
            #reptons =  numpy.arange(0, self.get_cfg().length + 1)
            reptons = self.get_connections().get_clear_range(connection)
        else:
            reptons =  numpy.arange(0, self.get_cfg().length + 1)            

#        if connection:
#            print 'Połączenie', connection.get_id()
#        else:
#            print 'Połączenie', 'BRAK'
#        print 'Reptony do updateu', reptons
            
        cis, trans = cfg.reptons_to_ranges(reptons)
#        print 'Odtwarza', cis, trans, getattr(cfg, 'cis'), getattr(cfg, 'trans')
#        print 'Istniejące obecnie', self.get_connections().show()
        #raw_input('')

        rr = {'cis': cis, 'trans': trans}
        for attr in rr.keys():
            # diff can be one of:
            # 0: slack; 1: taut +, -1 taut -
            if not rr[attr].size:
                continue

            # od jakiego indeksu (_f) do jakiego (_t) 
            # mam analizować łańcuch
            _f, _t = rr[attr][0], rr[attr][-1] + 1
          
            # współrzędna reptonu przed pierwszym analizowanym
            # potrzebna do określenia stanu linka
            base = getattr(cfg, attr)[_f-1] if _f > 0 else 0

            # translacja względem bazowego, dostajemy więdzę
            # o odległościach od bazowego
            _cfg = numpy.copy(getattr(cfg, attr)[_f:_t] - base)
            _cfg[1:] = _cfg[1:] - _cfg[:-1]
            yield attr, _cfg, _f, _t


    def rule_middlepoint(self, connection):
        rev = {'cis': 'trans', 'trans': 'cis'}
        cfg = self.get_cfg()
#        print 'MIDDLE'
        for attr, _cfg, _f, _t in self.get_update(connection):
            repr_split = [(i + _f, _cfg[i:i + 2]) for i in range(_cfg.size - 1) if numpy.logical_xor(*_cfg[i:i + 2])]
            for pos, rep in repr_split:
                change = rep[1] - rep[0]

                tst = numpy.copy(getattr(cfg, attr))
                
                tst[pos] += change

                if not self.can_exist(tst, pos, self.C_LIMIT):
                    continue

                #new_cfg = {attr: numpy.copy(getattr(cfg, attr)), rev[attr]: numpy.copy(getattr(cfg, rev[attr]))}
                #new_cfg[attr][pos] += change
                #rpr = Representation(**new_cfg)
                #if str(rpr).count('ooo'):
                #    print 'erro', cfg, ' ===> ', rpr, tst, change, new_cfg[attr]
                #    raw_input('')

                
                if  attr == 'cis':
                    repton_id = cfg.cis.size - 1 - pos
                else:
                    repton_id = cfg.cis.size + 2 + pos
#                print '\tZnajduje', Updater('M', attr, pos, change, repton_id).get_id(), pos, attr, repton_id
                yield Updater('M', attr, pos, change, repton_id)

    def rule_hernia(self, connection):
        cfg = self.get_cfg()
        actions = {-1: (1,), 1: (-1,), 0: (-1, 1)}
#        print 'HERNIA'
        for attr, _cfg, _f, _t in self.get_update(connection):
            repr_split = [(i + _f, _cfg[i:i + 2]) for i in range(_cfg.size - 1) if numpy.sum(_cfg[i:i + 2]) == 0]
            for pos, rep in repr_split:
                for change in actions[rep[0]]:

                    if getattr(cfg, attr)[pos] == 0 and change == -1:
                        continue

                    tst = numpy.copy(getattr(cfg, attr))
                    tst[pos] += change
                    if not self.can_exist(tst, pos, self.C_LIMIT):
                        continue

                    if  attr == 'cis':
                        repton_id = cfg.cis.size - 1 - pos
                    else:
                        repton_id = cfg.cis.size + 2 + pos

#                    print '\tZnajduje', Updater('H', attr, pos, change, repton_id)
                    yield Updater('H', attr, pos, change, repton_id)


    def rule_biaspoint(self, connection):
        cfg = self.get_cfg()
        rev = {'cis': 'trans', 'trans': 'cis'}
        prob = {'cis': 'F', 'trans': 'B'}
        repton_ids = {'cis': cfg.cis.size, 'trans': cfg.cis.size + 1}
        for attr in rev.keys():
            if getattr(cfg, attr).size and getattr(cfg, attr)[0] == 0:

                tst = numpy.zeros(getattr(cfg, rev[attr]).size + 1)
                tst[1:] += getattr(cfg, rev[attr])

                if not self.can_exist(tst, 0, self.C_LIMIT):
                    continue
                yield BiasUpdater(prob[attr], repton_ids[attr])

    def rule_switch(self, connection):
        cfg = self.get_cfg()
        rev = {'cis': 'trans', 'trans': 'cis'}
        prob = {'cis': 'UF', 'trans': 'UB'}
        #rept = {'cis': 0, 'trans': cfg.cis.size + cfg.trans.size}
        rept = {'trans': 0, 'cis': cfg.cis.size + cfg.trans.size}
        #print 'Testing SWITCH', cfg
        for attr in rev.keys():
            if not getattr(cfg, attr).size and getattr(cfg, rev[attr])[-1] - getattr(cfg, rev[attr])[-2] == 0:
                #print 'FOUND', JumpUpdater(prob[attr], rept[attr]), JumpUpdater(prob[attr], rept[attr]).get_id()
                yield JumpUpdater(prob[attr], rept[attr])

class OneDimRun(process.MCRun):

    POOL = 'POOL'


    def get_rnd(self, length):
        cis = [0]
        for i in range(length-1):
            pool = [0, 1]
            if cis[-1] > 0:
                pool.append(-1)
            choice = pool[numpy.random.randint(0, len(pool))]
            cis.append(cis[-1] + choice)
        return numpy.array(cis)

    def on_exit(self, samplers, step, dt, old_cfg, new_cfg, connection):
        pass

    def _on_exit(self, samplers, step, dt, old_cfg, new_cfg, connection):
        NAME = self.__class__.POOL
        if os.path.exists('./%s' % NAME):
            try:
                file_obj = open(NAME, 'rb')
                stored = pickle.load(file_obj)
                file_obj.close()
            except EOFError:
                stored = {}
        else:
            stored = {}

        if not stored.has_key(new_cfg.length):
            stored[new_cfg.length] = [{'cis': new_cfg.cis, 'trans': new_cfg.trans}]
        else:
            stored[new_cfg.length].append({'cis': new_cfg.cis, 'trans': new_cfg.trans})
        file_obj = open(NAME, 'wb')
        pickle.dump(stored, file_obj)
        file_obj.close()

    def get_from_pool(self, length):
        NAME = self.__class__.POOL
        if os.path.exists('./%s' % NAME):
            file_obj = open(NAME, 'rb')
            stored = pickle.load(file_obj)
            file_obj.close()
            pool = stored.get(length)
            # wyciągamy z puli ewentualny zapisane już wpisy
            # - jeżeli ich nie ma, to nie wycągamy...
            if pool is None:
                return None
            arch = pool[numpy.random.randint(0, len(pool))]
            cis = arch['cis']
            trans = arch['trans']
            rpr = Representation(cis, trans)
            return OneDimChain(rpr)

    def generate_state(self, **kwargs):
#        f_pool = self.get_from_pool(kwargs.get('length'))
#        if f_pool:
#            return f_pool
                                    
        # dlugosc 
        length_left = (kwargs.get('length') - 1)/2
        length_right = kwargs.get('length') - 1 - length_left
        while 1:
            # -----------------------------
            cis = self.get_rnd(length_left)
            trans = self.get_rnd(length_right)
            rpr = Representation(cis,trans)
            try:
                r = OneDimChain(rpr)
                return r
            except base.ValidationError, error:
                pass




            
                       
