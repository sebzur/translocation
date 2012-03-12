import sys
import numpy

def merge(pattern, min, max, r_max):
    data = []
    for N in range(min, max+1):
        for r in range(r_max):
            name = '%s%d_cR%d' % (pattern, N, r)
            print 'Opening', name
            last_line = numpy.loadtxt(name)[-1]
            J = last_line[1]/last_line[0]
            data.append(J)

    print data
    data = numpy.array(data)
    print "Mean: %f, std: %f, error: %f" % (data.mean(), data.std(), data.std()/numpy.sqrt(data.size))
    #print ["%.10f" % e for e in numpy.array(data).mean(axis=1)]
    #print ["%s" % round(e,4) for e in numpy.array(_data).mean(axis=1)]
    #print ["%.4f" % round(e,4) for e in numpy.array(_data).mean(axis=1)]
    #print '\t'.join([X,V,t,thr, "%.20f" % (float(V)/float(thr))])
    #merged.write('%d\t%s\n' % (i, '\t'.join([X,V,t,thr, "%.20f" % (float(V)/float(thr))])))
    #data_file.close()
    

if __name__ == '__main__':
    merge(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    #mean_j(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
          
