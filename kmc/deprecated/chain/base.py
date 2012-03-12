# -*- coding: utf-8 -*-
import numpy

class Connection(object):
    def __init__(self, states, name, dx, chain):
        self.name = name
        self.states = states
        self.chain = chain
        self.dx = dx

class DB():
    def __init__(self, cls):
        self.cls = cls

    def get_or_create(self, states):
        try:
            return self.cls(states)
        except Exception, error:
#            print error
            return None

class BaseChainMetaclass(type):
    def __init__(cls, name, bases, attrs, *args, **kwargs):
        # Manager objects should be accessible only via classes
        # (accesing via instances are forbidden (purity-related reasons)
        #print ">>>bases<<", bases, cls
        try:
            if BaseChain not in bases:
                return
        except NameError:
            return 

        #if not hasattr(cls, 'objects'):
        #    print 'Creating DB with class', cls
        #    cls.objects = DB(cls)

        # nadpisujemy ze względu na dziedziczenie
        cls.objects = DB(cls)

class BaseChain(object):
    __metaclass__ = BaseChainMetaclass

    def __new__(cls, *args, **kwargs):
        for i in (0, 1):
            # Aby utowrzuć obiekt w ogóle
            if numpy.any(numpy.cumsum(cls.states_to_vec(cls.get_side(i, args[0]))) < 0):
                message = 'The state %s can not be created!' % args[0]
                raise ValueError(message)

        # args[0] to stany
        

        D = len(args[0])-2
        #D = 8

        #LIMIT = 4
        #D = LIMIT if len(args[0]) > LIMIT else len(args[0])-2
        
        cls.filter_(args[0], D)
        return super(BaseChain, cls).__new__(cls)

    @classmethod
    def filter_(cls, states, D):
        # N - liczba slacków, na które nie pozwalamy
        # Przykładowo gdy N = 3 to nie pozwalamy na trzy i więcej kolejnych
        all_zero = 'o' * D
        for i in range(0, len(states) - D):
            if states[i:i+D] == all_zero:
                message = 'The state %s can not be created!' % states
                raise ValueError(message)


    def __init__(self, states='', *args, **kwargs):
        super(BaseChain, self).__init__(*args, **kwargs)
        self.states = states
        self.connections_build = False
        self.connections = []

    def __str__(self):
        return self.states

    def __eq__(self, other):
        return str(self) == str(other)

    @property
    def links_number(self):
        return len(self.states)

    @property
    def length(self):
        return sum(self.states_to_vec(self.states))

    @classmethod
    def states_to_vec(cls, states):
        """ Returns vector representation of states """
        raise NotImplementedError
    
    def get_moves():
        """ Return the tuple of the collables to call """
        raise NotImplementedError

    @classmethod
    def get_distance_from_wall(cls, side, states):
        """ Returns the distance of the last link from wall """
        return sum(cls.states_to_vec(cls.get_side(side,states)))

    @classmethod
    def get_side(cls, side, states):
        """ Returns the chain subset: 0 - left side, 1 - right side of the wall """
        states = states.split('p')[side]
        # To get the proper order, if user ask for left side (side=0)
        # we have to revert the chain configuration
        return states if side else states[::-1]

    def distance_from_wall(self, side):
        return self.__class__.get_distance_from_wall(side, self.states)

    def side(self, side):
        return self.__class__.get_side(side, self.states)



    # ------------------------------------------------------------
    # Velocity calculaitons
    # -----------------------------------------------------------

    def throughput(self,  prob):
        throughput = numpy.zeros(self.links_number)
        if not self.connections:
            self.build_transitions()
        for connection in [conn for conn in self.connections if conn.name in ('B', 'F', 'UF', 'UB')]:
            for i, dx in connection.dx:
                if connection.name == 'F':
                    throughput[i] += prob[connection.name]
                elif connection.name == 'B':
                    throughput[i] -= prob[connection.name]
                elif connection.name in ('UF', 'UB') and i==0:
                    throughput[0]= dx * prob[connection.name]
        return throughput

    def get_velocity_jump_dx(self, prob):
        if not self.connections:
            self.build_transitions()
        return sum([prob[connection.name] * self.length for connection in self.connections if connection.name in ('UF', 'UB')])

    def get_velocity_jump(self, prob):
        if not self.connections:
            self.build_transitions()
        return sum([prob[connection.name] for connection in self.connections if connection.name in ('UF', 'UB')])

    def get_velocity(self, prob):
        if not self.connections:
            self.build_transitions()

        the_array = numpy.zeros(self.links_number + 1)
        for connection in  self.connections:
            for dx in connection.dx:
                the_array[dx[0]] += dx[1] * prob[connection.name]
        return the_array

    def add_connection(self, segment, name, reversed, dx, symmetric = False):
        if segment.states not in [connection.states for connection in self.connections]:
            self.connections.append(Connection(segment.states, name, dx, segment))
            if symmetric:
                try:
                    n_dx = map(lambda v: (v[0], -v[1]),  dx)
                    segment.add_connection(self, reversed, name, n_dx)
                except Exception, error:
                    print '>>>', error
                    pass
        else:
            raise ValueError('Transition already present.')

    # ------------------------------
    def remove_connections(self, segment, propagate=True):
        return 
        # czysci pamiec...
        for i, conn in enumerate(self.connections):
            if conn.chain is not segment:
                if propagate:
                    conn.chain.remove_connections(segment, False)
                else:
                    self.connections.pop(i)
                    self.connections_build = False
#                del conn.chain

    def build_transitions(self, symmetric=False):
        count = 0
        if True:#not self.connections_build:
 #           self.connections = []
#            print "klasa:", self.__class__
            for method in self.get_moves():
                # superfast check?
                for transition_segment, name, reversed, dx in [(self.__class__.objects.get_or_create(segment_str), n, r, dx) for segment_str, n, r, dx in method() if segment_str not in [c.states for c in self.connections]]:
                    # get_or_create zwraca None jak nie mogło utworzyć stanu
                    if transition_segment:
                        try:
                            self.add_connection(transition_segment, name, reversed, dx, symmetric=symmetric)
                            count += 1
                        except Exception, error:
                            print 'Exception in connection handler', error
                            pass
            self.connections_build = True
        else:
            pass
            print '\t->Already have!'
        return count
