import numpy
import sys
from pylab import *
import correlation

def mean_j(pattern, min, max, r_max):
    #merged = open('%s' % pattern, 'w')
    data = []
    for i in range(r_max):
        _name = '%s%d_cR%dPP' % (pattern, max, i)
        print 'processing:', _name
        _last_line = numpy.loadtxt(_name)[1:,:2]
        Nc = _last_line[:,1]/_last_line[:,0]
        _last_line[:,1] = Nc
        data.append(numpy.array(_last_line))
#    plot(_last_line[1:,0], Nc)

    maxes = [numpy.array(row)[:,0].max() for row in data]
    print maxes

    X = numpy.arange(0, numpy.max(maxes), numpy.max(maxes)/4000)

    inter = dict([(x,[]) for x in X])
    print len(data)
    for row in data:
        for a, b in row:
            for edge in X:
                if edge >= a:
                    #print 'Dodaje', edge, a
                    inter[edge].append(b)
                    break
        for edge in X[numpy.where(X>row[-1][0])]:
            inter[edge].append(0)

    for k,v in inter.iteritems():
        inter[k] = mean(v) if v else None
#    print inter


    #numpy.savetxt('www', numpy.array([(x,inter[x]) for x in X if inter[x]]))
    #numpy.savetxt('www_2', data[0])

    d = numpy.array([(x,inter[x]) for x in X if inter[x]])
    plot(d[:,0],d[:,1], linewidth=2, color='red')
    for row in data:
        r = numpy.array(row)
        plot(r[:,0],r[:,1], ':', alpha=0.3, color="#C9BFAF")

    xlabel('Time')
    ylabel('Current (dL/dT)')
    show()

#    numpy.savetxt('%s_%d_R_%d_satu' % (pattern, max, r_max), Nc)
#    show()

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
    mean_j(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    #get_cor(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    
