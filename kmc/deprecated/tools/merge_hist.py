import numpy
import sys
#from pylab import *
import correlation

def mean_j(pattern, min, max, r_max):
    #merged = open('%s' % pattern, 'w')
    data = []
    _name = '%s%d_cR%dPP' % (pattern, max, r_max)
    _last_line = numpy.loadtxt(_name)#[-1]
    Nc = _last_line[1:,-1]/_last_line[1:,-2]
    #hist(Nc, bins=1000, normed=True)
    #plt.axis([0.14, 0.20, 0, 1])
    plot(_last_line[1:,-2], Nc)
    numpy.savetxt('%s_thermal' % pattern, Nc)
    show()

def get_cor(pattern, min, max, r_max):
    #merged = open('%s' % pattern, 'w')
    data = {}
    for i in range(min, max):
        data[i] = []
        for j in range(r_max):
            _name = '%s%d_cR%dPP' % (pattern, i, j)
            print 'Processing', _name
            _last_line = numpy.loadtxt(_name)
            Nc = _last_line[1:,-1]/_last_line[1:,-2]
            z = correlation.Correlogram(data=Nc)
            x = z.get_zero(20000, 0.05)
            print 'X is:', x[0],x[1],x[0]/(len(Nc)+0.0)
            
            data[i].append([x[0],x[1],x[0]/(len(Nc)+0.0)])
    for i in range(min, max):
        print i, numpy.array(data[i])[:,0].mean(), numpy.array(data[i])[:,1].mean(), numpy.array(data[i])[:,2].mean()


if __name__ == '__main__':
    #merge(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    #mean_j(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    get_cor(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    
