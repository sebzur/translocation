#! /bin/bash
#c=$1
#for e in `LC_CTYPE="en_EN.UTF-8" seq 100 500 25000`
#for period in `LC_CTYPE="en_EN.UTF-8" seq 50 100 2000`
#for N in 12 15 17 20 25 50 75 100
for N in 5
    do
        for eps in 0.01 0.5 1 2 3.5 5 7 10 20 30
	do
<<<<<<< TREE
	    #mpirun -n 43 --hostfile hostfile python mpiruns.py -n $N -s 1000000 -r 43 -c 0.5 -e $eps
	    #mpirun -n 39 --hostfile hostfile python mpiruns.py -n $N -s 100000 -r 39 -c 0.0 -e $eps
	    mpirun -n 16 python mpiruns.py -n $N -s 100000 -r 16 -c 0.5 -e $eps
=======
	    #mpirun -n 43 --hostfile hostfile python mpiruns.py -n $N -s 1000000 -r 43 -c 0.0 -e $eps
	    python singlerun.py 5 $eps 50000
>>>>>>> MERGE-SOURCE
	done
    done
