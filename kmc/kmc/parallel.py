# -*- coding: utf-8 -*-
import numpy
from mpi4py import MPI
import time
import itertools

comm = MPI.COMM_WORLD
sub_comm = MPI.COMM_WORLD.Clone()
rank = comm.Get_rank()
size = comm.Get_size()


class ParallelMC(object):

    def run(self, prob, steps, repeats, run_cls, smpl_classes, **kwargs):
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
        results = self.run_thread(prob, steps, n_repeats, run_cls, smpl_classes, **kwargs)

        # Gathering the results (which is the dictionary)
        results_collected = comm.gather(results, root=0)
        self.process_results(results_collected, prob, steps, repeats, smpl_classes, **kwargs)


    def run_thread(self, prob, steps, n_repeats, run_cls, smpl_classes, **kwargs):
        start_time = time.time()
        results = []
        for repeat in xrange(int(n_repeats)):
            results.append(run_cls().run(prob, steps, smpl_classes, **kwargs))
        delta = time.time() - start_time
        return results


    def process_results(self, results, prob, steps, repeats, smpl_classes, **kwargs):
        """ Każda z klas samplujących musi implementować metodę merge, której zadaniem
        jest przyjęcie wyników pochodzących od innych samplerów tej samej klasy i połączenie ich
        """
        if rank == 0:
            # Jeżeli jestem w masteerze results ma strukturę
            # tabela "n" elementów, gdize n to liczba nodów liczących
            # każdym elemencie znajduje się "k" przeliczonych wyników
            # tak, że n*k daje łącznie liczbę repet
            for i, sampler_class in enumerate(smpl_classes):
                merged = []
                for result in results:
                    for own_result in result:
                        merged.append(own_result[i])
                sampler_class.merge(merged, prob, steps, repeats, **kwargs)
