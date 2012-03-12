# -*- coding: utf-8 -*-
import numpy
from mpi4py import MPI
from chain import onedim, twodim
import time
import itertools

comm = MPI.COMM_WORLD
sub_comm = MPI.COMM_WORLD.Clone()
rank = comm.Get_rank()
size = comm.Get_size()





class MonteCarlo(object):
    """ MC sampler - główna klasa realizująca symulację """
    def __init__(self):

    def run(self, prob, repeats, steps, length, dimension, period):
        """ Realizuje proces MC ... na razie nic więcej nie pamiętam... """
        # ------------------------
        # Definiujemy wektor, który dla każdemu nodowi określi 
        # liczbę powtórzeń, które ma wykonać.
        if rank == 0:
            # obliczenia te robimy tylko będąc masterem, 
            equal = numpy.ones(size) *  int(repeats/size)
            for i in range(repeats % size):
                equal[i] += 1
            n_repeats = equal
        else:
            n_repeats = None

        # ------------------------------
        # Po rozprowadzeniu w poprzednich kilku wierszach infa
        # ile razy każdy z nodów ma liczyć, teraz każdy z nodów
        # odbiera tę informację
        # ------------------------------
        n_repeats = comm.scatter(n_repeats, root=0)

        # -----------------------------
        # Generating local (node-wise) eigenvector part
        # Uruchamiamy obliczenia - na każdym z nodów realizowana jest 
        # metoda run_thread, której zadanie to przeprowadzenie n_repeats powtórzeń
        # każde powtórzenie ma steps kroków
        # -------------------------------
        results = self.run_thread(n_repeats, steps, prob, length, dimension, period)

        # Gathering the results (which is the dictionary)
        results_collected = comm.gather(results, root=0)
        self.process_results(results_collected, repeats, steps, dimension, length, prob, period)

    def run_thread(self, n_repeats, steps, prob, length, dimension, period):
        # Inicializacja wszystkich samplerów podanych do sampler_classes w konstruktorze
        samplers = [[sampler_cls(n_repeats, steps, length, dimension, prob, rank, period) for sampler_cls in self.sampler_classes] for rep in range(int(n_repeats))]
        start_time = time.time()
        
        for repeat in xrange(int(n_repeats)):


            MC().run(samplers[repeat], repeat)
            #results = self.sample(samplers[repeat], repeat, step, dt, current_state, new_state, connection)
                
        delta = time.time() - start_time
        for sampler in itertools.chain(*samplers):
            sampler.prepare_to_return()
        return samplers



    def process_results(self, results, repeats, steps, dimension, length, prob, period):
        """ Każda z klas samplujących musi implementować metodę merge, której zadaniem
        jest przyjęcie wyników pochodzących od innych samplerów tej samej klasy i połączenie ich
        """
        if rank == 0:
            # Jeżeli jestem w masteerze results ma strukturę
            # tabela "n" elementów, gdize n to liczba nodów liczących
            # każdym elemencie znajduje się "k" przeliczonych wyników
            # tak, że n*k daje łącznie liczbę repet
            for i, sampler_class in enumerate(self.sampler_classes):
                merged = []
                for result in results:
                    for own_result in result:
                        merged.append(own_result[i])
                sampler_class.merge(merged, repeats, steps, dimension, length, prob, period)
            

if __name__ == "__main__":
    B = 2.00
    prob = {'B': 1.0/B,'F': B, # backward & forward directions
            'UB': 1.0/B, 'UF': B, # jump-around probs
            'E': 1.0, # end links prob
            'M': 1.0, # middle
            'H': 0.5, # hernia cration
            'C': 0.0  # sideway motions
            }

    length = 400
    dim = 1
    m_c = MonteCarlo([]) # no saplers in testcase
    eig = m_c.run(prob, 10, 10000, length, dim)
    #eig = m_c.run(prob, 30, 100, length+1)
    #if rank == 0:
    #    translocation = Translocation(objects)
        #print eig
    #    print translocation.get_translocation_time(prob, eig)
















