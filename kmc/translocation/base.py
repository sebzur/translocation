# -*- coding: utf-8 -*-
import sys
import numpy

sys.path.append('/magazyn/SEBZUR/bazaar/KMC/dev')
from kmc import base
import itertools


class CPool(base.ConnectionPool):

    def __init__(self, length):
        self.length = length
        self.connections = self.get_clean_storage()

    def get_clean_storage(self):
        return {}

    def create(self, connection):
        # potraktowanie self.connections jako słownika, przy jednoczesnym
        # założeniu, że do danego stanu prowadzi z danej konfiguracji jedna i tylko
        # jedna drogra załatwia sprawę dubli w połączeniach
        
        #self.connections["%s%s%s" % (rate, pos.repton_id, pos.repton_move)] = base.Connection(cfg, rate, pos)
        #self.connections[str(cfg)] = base.Connection(cfg, rate, pos)

        try:
            for el in self.connections[connection.get_handled_repton()]:
                if el.get_id() == connection.get_id():
                    return
            
            self.connections[connection.get_handled_repton()].append(connection)
        except KeyError:
            self.connections[connection.get_handled_repton()] = [connection]

    def __iter__(self):
        return itertools.chain(*[self.connections[pos] for pos in self.connections])
        #return itertools.chain(*[self.connections[pos].values() for pos in self.connections])
        #return itertools.chain(self.connections.values())

    def show(self):
        return [[k, [c.get_id() for c in v]] for k,v in self.connections.iteritems()]
    
    def show_id(self):
        return list(itertools.chain(*[[c.get_id() for c in v] for k,v in self.connections.iteritems()]))
            
    def clear(self, connection):
#        print 'Będę usuwał, obcenie istniejące to:', self.show()
 
#        self.connections = {}
#        return

        if connection:
#            print 'Mam połączenie', connection.get_id(), self.get_clear_range(connection)
            cr = self.get_clear_range(connection)
            for i in cr:
                try:
                    self.connections.pop(i)
                except KeyError:
                    pass

    def get_clear_range(self, connection):
        #return  numpy.arange(0, 6)
        #LAST = 10

        # liczba linków powiększona o jeden + 1 bo w range nie wchodzi
        # górny limit
        #LAST = self.length + 1 + 1
        LAST = self.length + 1 + 1

        if connection.get_rate() in ['UF', 'UB', 'B', 'F']:
            # B i F mogą być obsłużone tak, żeby nie trzeba było przeliczać..
            return  numpy.arange(0, LAST)

        LIMIT = 4
        start = connection.get_handled_repton() - LIMIT 
        if start < 0:
            start = 0
        end = connection.get_handled_repton() + LIMIT# + 1
        if end > LAST:
            end = LAST
        return numpy.arange(start, end + 1)


class Chain(base.Configuration):
    pool_class = CPool
    C_LIMIT=3

    def get_validators(self):
        return [self.validate_distance, self.validate_st, self.validate_C]

    def validate_distance(self, cfg, **kwargs):
        if numpy.any(cfg.cis < 0) or numpy.any(cfg.trans < 0):
            raise base.ValidationError("przecina sciane")

    def validate_st(self, cfg, **kwargs):
        A = numpy.all(numpy.abs(cfg.cis[1:] - cfg.cis[:-1]) < 2)
        B = numpy.all(numpy.abs(cfg.trans[1:] - cfg.trans[:-1]) < 2)
        if not A and B:
            raise base.ValidationError("Nie możę być niejedynek")

    def validate_C(self, cfg, **kwargs):
        for side in ('cis','trans'):
            for i in range(getattr(cfg, side).size):
                ce = self.can_exist(getattr(cfg, side), i, self.C_LIMIT)
                if not ce:
                    raise base.ValidationError("Za duzo reptonow w komorce")
        

    def can_exist(self, cfg, pos, C):
        return can_exist(cfg, pos, C)


def can_exist(cfg, pos, C):
    acc = 1
    LOW = pos - C  if pos - C  > 0 else 0

    left = cfg[LOW:pos][::-1]  
    right = cfg[pos+1:pos+C+1] if cfg.size - 1 > pos else []

    if pos - C <= 0 and cfg[0] == 0:
        left = cfg[LOW:pos][::-1].tolist() + [0]


    for side in (left, right):
        for position in side:
            if position == cfg[pos]:
                acc += 1 
            else:
                break

    return acc <= C 
