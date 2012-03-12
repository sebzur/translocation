import sys
import numpy

def parse(prefix, repeat_from, repeat_to, n_from, n_to, dim):
    output = []
    for n in range(n_from, n_to):
        print (repeat_to-repeat_from, n + 1)
        data = numpy.zeros((repeat_to-repeat_from, n + 2))
        for i,r in enumerate(range(repeat_from, repeat_to)):
            print 'REading:'
            name = '%s_R%s_S1000000_B2.00_H0.50_N%s' % (prefix, r, n)
            the_file = open(name, 'r')
            all_data = the_file.readlines()
            print 'read..'
            #dT, dL, dX = numpy.array(map(float, the_file.readlines()[-1].split()[:-1]))[:3]
            tmp = numpy.array([map(float, line.split()[:-1]) for line in all_data])
            a, b = numpy.polyfit(tmp[:,0], tmp[:,1], 1)
            print 'Fit:', a, b
            data[i, 0] = a * n
#            print n, dT, dL, dX, dT/dL*n, dX/dT
            the_file.close()

        vi = data[:,1:].mean()
        vi_error = data[:,1:].std()/numpy.sqrt(data.shape[0]*(data.shape[1]-1))
        J=data[:,0].mean()
        J_error = data[:,0].std()/numpy.sqrt(data.shape[0])
        tc = n/J
        add = [n, J, J_error, vi, vi_error, tc]
        print "n J J_e vi vi_e tc"
        print add
        output.append(add)
        print output

    numpy.savetxt("%s_data" % prefix, output)
    print output

if __name__ == "__main__":
    parse(sys.argv[1],*map(int, sys.argv[2:]), dim=1) 

