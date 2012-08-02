import numpy as np
import sys


#polozenia z pliku jako tablica np.array nx3
def from_mola(pos):
    positions = np.array(pos).reshape(len(pos)/3,3)
    return positions
    
    
#calculate distance between neigbouring reptons in a given configuration and return result as array
def r2r_distance(conf):
    diff = np.diff(conf, axis=0)
    sqr = diff**2
    length = np.sqrt(sqr.sum(axis=1))
    return  length

#calculate tranlation vectors for all reptons between two given configrations and return as array
def t_vet(conf_old, conf_new):
    k = conf_new - conf_old
    return k

    
# check if given array of transation vector - conf - has only allowed translaction from translations array
def check_vectors(conf, translations):
    for step in conf:
        #print step
        k = np.any ([ (step  == x).all() for x in translations])
        if not k:
            return False
    return True
    
#some function to analize data
def calculate_cms(conf):
    return conf.sum(axis=0)/conf.shape[0]
    
    
def check_polimer(data, length, translations):
    for idx in np.arange(0,data.shape[0]-1):
        conf_old = from_mola(data[idx][1:])
        conf_new = from_mola(data[idx+1][1:])
        t = t_vet(conf_old, conf_new)
        print idx
        if  np.any(r2r_distance(conf_old) > length):
            print "Rozerwany"
            break

        if not check_vectors(t, translations):
            print idx, " Zla translacja !!!!!"
            print "Z  : ", [i for i in data[idx][1:]]
            print "DO : ", [i for i in  data[idx+1][1:]]
            print "Przez: ",t
            break

def check_countour(conf_old, conf_new):
    t = t_vet(conf_old, conf_new)
    indx = -1
    for idx, val in enumerate(t):
        if np.any( val != [0,0,0] ):
            indx = idx
            break
    
    if indx == 0 or indx == t.shape[0] -1:
        return True
        
    else:
        #sprawdz czy po konturze - czyli czy po translacji jest na pozycji sasiedniego
        if np.all(conf_new[indx] == conf_new[indx-1]) or np.all(conf_new[indx] == conf_new[indx+1]):
            return True
        print "NIE PO KONTURZE"
        return False
    
    
def check_C(data, C):
    for idx in np.arange(0,data.shape[0]-1):
        conf_old = from_mola(data[idx][1:])
        k = r2r_distance(conf_old)
        ile =0
        for i in k:
            
            if i == 0:
                ile += 1
            else:
                ile = 0
            if ile >= C:
                print "Zlamane C = ", C
                print k
                return False
    return True
                


            
if len(sys.argv)>1: 
    data = np.loadtxt(sys.argv[1])
else:
    data = np.loadtxt('p.pos')

#translations = np.array( [ [1,0,0], [-1,0,0], [0,1,0], [0,-1,0],[0,0,0]])

#check_polimer(data,1,translations)
        
#check_C(data, 2)

print "CALCULATE"


for idx in np.arange(0,data.shape[0]-1):
    conf_old = from_mola(data[idx][1:])
    conf_new = from_mola(data[idx+1][1:])
    check_countour(conf_old, conf_new)



#window = 20
#hist = np.zeros(window)

#counter = 0

#for idx in np.arange(0,data.shape[0]-1 - window):
    #if idx % 100 == 0 :
        #print idx
    #conf1 = from_mola(data[idx][1:])
    #cms1 = calculate_cms(conf1)
    
    #for i in np.arange(1, window):
        #conf2 = from_mola(data[idx+i][1:])
        #cms2 = calculate_cms(conf2)
        #diff = cms2 - cms1
        #diff2 = diff**2
        #hist[i] += diff.sum()
    #counter += 1

#hist = hist/counter

#print hist
    #conf_old = from_mola(data[idx][1:])
    #x,y,z = calculate_cms(conf_old) 
    #print x, y, z
    
    

