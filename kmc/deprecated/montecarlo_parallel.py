# -*- coding: utf-8 -*-
import numpy
from mpi4py import MPI
from chain import onedim, twodim
from stochastics import Translocation
import time
import itertools
import progres

comm = MPI.COMM_WORLD
sub_comm = MPI.COMM_WORLD.Clone()
rank = comm.Get_rank()
size = comm.Get_size()


class MonteCarlo(object):
    """ MC sampler - główna klasa realizująca symulację """
    def __init__(self, sapler_classes):
        # samler_classes - lista zawierająca klasy (implementujące interfejs 
        # deklarowany przez bazową klasę 'Sampler'), które zostaną użyte w proces
        # samplowania do pobierania informacji
        self.sampler_classes = sapler_classes

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

    def sample(self, samplers, repeat, step, dt, current_state, new_state, connection):
        """ Sygnalizuje wszystkim samplerom zawartym w liście 'samplers', że można by coś
         w końcu policzyć - wywołuje po kolei każdego, podając mu na wejściu informacje.

         Każdy z samplerów powinien lokalnie zarządzać pamięcią - obiekty te są lokalnie 
         (w sensie na poziomie wątku MPI) tworzone i trzymane przez cały czas pracy symulacji.

         """
        for sampler in samplers:
            sampler.sample(repeat, step, dt, current_state, new_state, connection)

    def run_thread(self, n_repeats, steps, prob, length, dimension, period):
        # Inicializacja wszystkich samplerów podanych do sampler_classes w konstruktorze
        samplers = [[sampler_cls(n_repeats, steps, length, dimension, prob, rank, period) for sampler_cls in self.sampler_classes] for rep in range(int(n_repeats))]
#        if rank == 0:
#            prog = progres.ProgressBar(0, n_repeats * steps, 77, mode='fixed', char='#')
        start_time = time.time()
        
        BASE_B = prob['F']
        for repeat in xrange(int(n_repeats)):
            # Pętla iterująca po wymaganej liczbie powtórzeń - na początku każdego powtórzenia
            # genrujemy losową konfigurację startową - tutaj jest punkt, gdzie można by podpiąć
            # zapisywanie końcowej (ztermalizowanej) kofiguracji i ją wykorzystać...
            current_state = self.generate_state(length, dimension)
            # licznik calkowitego czasu
            total_time = 0
            for step in xrange(steps):
                # =========================================
                # każdy krok składa się z następujących elementów:
                # - szukaj wszystkich możliwych przejść z konf. bieżącej
                # - wyznacz czas życia tej konfiguracji
                # - wylosuj nowy stan 
                # - przekaż info do saplerów
                # - ustaw nowy stan jako bieżacy i kontynuuj
                # =========================================
                
                # -------------------------------
                # Generujemy przejścia
                current_state.build_transitions()
                # -------------------------------
                
                # modyfikujemy prawd

                #prob['F'] = BASE_B * numpy.abs(numpy.sin(step * 0.1))

                # -------------------------------
                # Wyznaczamy czas życia
                A = sum([prob[connection.name] for connection in current_state.connections])
                # See: http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.lognormal.html#numpy.random.lognormal
                r = numpy.random.random()
                dt = -numpy.log(r)/A
                total_time += dt
                #dt = 1.0/A
                # -------------------------------

                # -------------------------------
                # Wyznaczamy nowy stan
                new_state, connection = self.select_segment(current_state.connections, prob, A)
                # -------------------------------

                # -------------------------------
                # przekazujemy info samplerom
                results = self.sample(samplers[repeat], repeat, step, dt, current_state, new_state, connection)
                # -------------------------------

                # -------------------------------
                # Ustwiamy nowy stan jako bieżacy
                current_state = new_state
                # ------------------------------
                
        delta = time.time() - start_time
        for sampler in itertools.chain(*samplers):
            sampler.prepare_to_return()
        return samplers

    def select_segment(self, connections, prob, A):
        """ Wybiera konfigurację do której przejdziemy, korzystając 
        z drabinki prawd."""
        cumulated_probs = numpy.array([prob[connection.name] for connection in connections]).cumsum()
        rand_num = numpy.random.uniform(0, cumulated_probs[-1])
        for prob_value, connection in zip(cumulated_probs, connections):
            if rand_num <= prob_value:
                return connection.chain, connection

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
            
    def generate_state(self, length, dimension):
        dimension_atoms = {2: ('o', 'S', 'N', 'E', 'W'),
                           1: ('o', '+','-')}
        objects = {1: onedim.OneDimChainSisters.objects, 
                   #1: onedim.OneDimChainShifted.objects,
                   2: twodim.TwoDimChain.objects
                   }

        state = None
        while state is None:
            representation = ''.join([dimension_atoms[dimension][numpy.random.randint(0, len(dimension_atoms[dimension]))] for i in range(length-1)])
            cut_at = numpy.random.randint(0, length)
            generated = representation[:cut_at] + 'p' + representation[cut_at:]
            state = objects[dimension].get_or_create(states=generated)
        return state

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
