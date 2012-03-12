# -*- coding: utf-8 -*-
import numpy
import itertools
import copy
import pickle
import os

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Connection(object):
    """ Represents the way the configuration can reconfigure to another.

    This class instances are designed to be members of ConnectionPool instances, where it should
    be stored somehow. ConnectionPool is attached (is a member) of Configuration instance and defines
    (via the membership) the way the configuration can reconfigure.

    """

    def __call__(self, configuration, **kwargs):
        raise NotImplementedError
        
    def get_rate(self, **kwargs):
        raise NotImplementedError


class ConnectionPool(object):

    def __iter__(self):
        raise NotImplementedError

    def clear(self, through):
        # Metoda wykonywana zawsze po znalezieniu nowej konfiguracji
        # jej zadaniem jest usinięcie niepotrzebnych
        raise NotImplementedError

    def create(self, cfg, rate, extra):
        raise NotImplementedError

class ConfigurationABC(object):
    """ Defines the interface the subclasses must implement """

    def get_rules(self):
        """ Return the callable objects responsible for the moves definitions.

        Each class subclassing this class have to implemente `get_rules` that returns
        the iterable set of callable objects, each object in the set will be asked to generate the 
        connections from the current state to the new possible states.

        Callable definition
        ---------------------
        Each callable will be call with one argument, that will be the connection (Connection class
        instance) that was used to generate the current state. Thus, the callable has to be designed
        to work in a specific way:
        - if the connection argument *is not* provided, it should returns all possible connections
        from this statet to others
        - if connection *is provided*, it should returns only the connections that are created due to the
        reconfiguration.

        The collable have to returns a tuple of three elements:
        - new configuration
        - transition rate (probability over time)
        - the information on what is changed in the present cfg if this connection will happens


        Example definition of rule
        -------------------------------
        This is very dummy definition of connection finder, that is doing nothing
        - the state will simply stay where it was for ever.

        def find_connection(self, connection, **kwargs):
            return self.cfg, 'N', None
        """
        
        raise NotImplementedError
    
    def get_validators(self):
        """ Returns the set of callable objects that will test, if the cfg should be considered
        as valid configuration, optionaly with respect to **kwargs.

        Callable definition
        ---------------------
        Each callable will be called with cfg and **kwargs and should return cfg if it is valid,
        or raise ValidationError with a proper message, if its not valid.

        Example definition of validator
        -------------------------------

        def validate(self, cfg, **kwargs):
           # assuming, that cfg is iterable:
           if len(cfg) < 10:
              return cfg
           raise ValidationError('The CFG is to short')


        """
        raise NotImplementedError

class Configuration(ConfigurationABC):
    pool_class = ConnectionPool

    def __init__(self, configuration, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)
        # Let's check if theres everything correct
        # with the initial configuration
        error = self.validate(configuration, **kwargs)
        if error :
            raise ValidationError('Configuration %s is disallowed! Reason: %s'% (configuration, error))

        # cfg to dowolny obiekt reprezentujący konfigurację
        self.cfg = configuration
        # connections to pula połączeń
        self.connections = self.pool_class(self.cfg.length)

        # Początkowa inicializacja połączeń
        self.update_connections(through=None)

    def __str__(self):
        return self.cfg

    # ------------------------------------
    # Setters/Getters
    # ------------------------------------

    def get_connections(self):
        return self.connections

    def set_cfg(self, cfg):
        self.cfg = copy.deepcopy(cfg)
        #self.cfg = cfg

    def get_cfg(self):
        return self.cfg

    # ------------------------------------
    # Connection handlers
    # ------------------------------------

    def update_connections(self,  through, **kwargs):
        # Na razie zakładamy, że system działą tylko w jeden sposób - zawsze zostawia
        # połączenia - doecelowy byłobyto konfigurowalne
        self.get_connections().clear(through, **kwargs)
        for method in self.get_rules():
            for operator in method(through, **kwargs):
                self.get_connections().create(operator)

    def validate(self, cfg, **kwargs):
        for validator in self.get_validators():
            try:
                validator(cfg, **kwargs)
            except ValidationError, error:
                return error
            
        # If all validation rulles passes without exception,
        # we're returngin that evertything is correct
        return None
    # ------------------------------------
    # KMC specific methods
    # ------------------------------------

    def get_lifetime(self, prob):
        """ Returns state life-time.

        Lifetime is calculated with respect to total branching ratio of the state, which means, that
        we need the information on every possible state that this state can break into.

        """
        A = sum([prob[connection.get_rate()] for connection in self.get_connections()])
        # See: http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.lognormal.html#numpy.random.lognormal
        r = numpy.random.random()
        return -numpy.log(r)/A


    def select_connection(self, prob):
        """ Returns the connection that will be choosen for the reconstructing of this state.

        Returned values are:
        - connection: the connection choosen as the reconstructor
        - prob_value: the value of the probability for the reconstructor to be selected
        - rand_num: the value of the probability rate that decided that the connection was selected

        """
        cumulated_probs = numpy.array([prob[connection.get_rate()] for connection in self.get_connections()]).cumsum()
        rand_num = numpy.random.uniform(0, cumulated_probs[-1])
        for prob_value, connection in zip(cumulated_probs, self.get_connections()):
            if rand_num <= prob_value:
                return connection

    def reconfigure(self, prob):
#        print '==' * 10
#        print 'REKONFIGURACJA', self.get_cfg()


        connection = self.select_connection(prob)
        # connection to obiekt wywoływalny, który w argumencie dostaje
        # obiekt reprezentujący konfigurację
        connection(self.get_cfg())
#        print 'Wybrane połączenie', connection.get_id()
#        print 'NOWA:', self.get_cfg()
        self.update_connections(connection)
#        print '==' * 10

#        print 'NOWA:', self.get_cfg()
#        print '==' * 10
        NAME = 'connections_9'
        if 0:
            if 0:
                if os.path.exists('./%s' % NAME):
                    file_obj = open(NAME, 'rb')
                    stored = pickle.load(file_obj)
                    file_obj.close()
                else:
                    stored = {}
                key = str(self.get_cfg())
                if not key in stored:
                    #if 'U' in map(lambda x: x[0], self.get_connections().show_id()):
                        #print 'Storing', key
                        #print 'Mam cfg', self.get_cfg(), self.get_connections().show_id()
                        #raw_input('')
                    stored[key] = self.get_connections().show_id()
                    #print '\t', stored[key]
                    file_obj = open(NAME, 'wb')
                    pickle.dump(stored, file_obj)
                    file_obj.close()

            else:
                file_obj = open(NAME, 'rb')
                stored = pickle.load(file_obj)
                file_obj.close()
                key = str(self.get_cfg())

                valid = stored.get(key)
                if valid:

                    for c in self.get_connections().show_id():
                        if c not in valid:
                            print 'KEY:', key
                            print 'Stare', valid
                            print 'Nowe', self.get_connections().show_id()
                            raw_input('NIEROWNO')

                    for v in valid:
                        if v not in self.get_connections().show_id():
                            print 'SYMMM'
                            print 'KEY:', key
                            print 'Stare', valid
                            print 'Nowe', self.get_connections().show_id()
                            raw_input('NIEROWNO')



        return connection, self.get_cfg()


class DummyCfg(Configuration):
    
    def get_rules(self):
        return (self.dummy_move,)

    def get_validators(self):
        return (self.dummy_validator, )

    def dummy_move(self, through):
        yield self.cfg, 'A', 0

    def dummy_validator(self, cfg, **kwargs):
        return True


if __name__ == "__main__":
    cfg = DummyCfg('aaa')
    for i in range(3):
        cfg.reconfigure({'A': 1})

        

