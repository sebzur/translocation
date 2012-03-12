import os
import sys
import numpy
from matplotlib import pyplot

class Correlogram(object):
    def __init__(self, data = None):
        self.data = data

    def autocov(self, signal, lag):    
        n = len(signal)    
        mean = signal.mean()
        a_mean = signal[:n-lag].mean()
        b_mean = signal[lag:].mean()
        c_mean = signal[:n].mean()
        return ((signal[:n-lag]-a_mean)*(signal[lag:]-b_mean)).sum()/((signal[:n]-c_mean)**2).sum()   

    def acvf(self, end):
        return numpy.array([ [lag, self.autocov(self.data,lag)] for lag in range(end)])

    def get_zero(self, end, error = 0.1):
        data = self.acvf(end)
        for element in data:
            if element[1] < error:
                return element[0], element[1]

        ind = numpy.nanargmin(numpy.abs(data[:, 1]))
        return data[ind]

    def plot_acvf(self, end):
        data = self.acvf(end)
        pyplot.subplot(211)
        pyplot.plot(data[:,0],data[:,1])
        pyplot.plot(data[:,0], data[:,1])
        
        pyplot.subplot(212)
        pyplot.plot(self.data)
        pyplot.show()

    def plot_signal(self):
        pyplot.plot(self.data)
        pyplot.show()
        

def get_random_signal():
    lens = 1000
    x = numpy.linspace(0,100, lens)
    y = numpy.sin(x)*19
    s = 100
    for i in range(3909):        
        pos = int(lens*numpy.random.rand())
        if pos<lens-s:
            y[pos:pos+s] = y[pos:pos+s] + numpy.random.randint(-4,4,s)
    return y
        
        
if __name__ == "__main__":
    d = numpy.loadtxt(sys.argv[1])

    c = Correlogram(data=d)
    c.plot_acvf(20000)
    
