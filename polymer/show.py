#! /usr/bin/python
# -*- coding: utf-8 -*-
from visual import *
from visual.graph import *
from string import *
import sys

if len(sys.argv)>1: plik=sys.argv[1]
else:plik='polimer.pos'
print plik

win=500
gray=(0.7,0.7,0.7)
L=10

#jak sie mu nie poda range, to bedzie na biezaco skalowal scene
#scene = display(title="Klaster",width=win,height=win,x=0,y=0,range=2*L,center=(0.0,0.0,0.0))
scene = display(title="Klaster",width=win,height=win,x=0,y=0,range=6*L,center=(0.0,0.0,0.0), background=color.black)


try:
        
	inp=open(plik,'r')
	mols=[]
        lines=[]
        
	arrow(pos=(0,0,0), axis=(1,0,0))
	arrow(pos=(0,0,0), axis=(0,1,0), color=color.red)
	arrow(pos=(0,0,0), axis=(0,0,1), color=color.blue)
	
	wiersz=inp.readline()
	w=wiersz.split()

	krok=float(w[0])
    
        tail = (len(w)-1)/3
	
	for i in range(0,(len(w)-1)/3):
                if i==0:
                    mols.append(sphere(pos=(atof(w[1+i*3]),atof(w[2+i*3]),atof(w[3+i*3])),radius=0.4,color=color.blue))
                elif i==tail-1:
                    mols.append(sphere(pos=(atof(w[1+i*3]),atof(w[2+i*3]),atof(w[3+i*3])),radius=0.35,color=color.yellow))
                else:
                    mols.append(sphere(pos=(atof(w[1+i*3]),atof(w[2+i*3]),atof(w[3+i*3])),radius=0.3,color=color.red))
        #polacz               
        linie = curve( pos=[ i.pos for i in  mols], radius=0.1, color=color.green)   
            
            
		    
except:
	inp.close()
	sys.exit(1)



while 1:
	rate(10)
	
	try:
		wiersz=inp.readline()
   		if not wiersz:
			rate(0.5)
			continue
		w=wiersz.split()
		
		krok=float(w[0])
	       
		
		for i in range(0,(len(w)-1)/3):
			mols[i].pos=(atof(w[1+i*3]),atof(w[2+i*3]),atof(w[3+i*3]))	
			
                linie.pos = [ i.pos for i in  mols]
	except:pass
	
inp.close()



#for wiersz in inp.readlines():
#	rate(100)
#	w=wiersz.split()
#
#	krok=int(w[0])
#	for i in range(0,(len(w)-1)/3):
#		mols[i].pos=(w[1+i*3],w[2+i*3],w[3+i*3])
