# -*- coding: utf-8 -*-
import numpy

class Translocation(object):
    def __init__(self, objects):
        self.objects = objects

    def get_translocation_time(self, prob, eigenvector):
        #print eigenvector
        vel_jump_dx = self.get_velocities_jump_dx(prob, eigenvector)
        vel_jump = self.get_velocities_jump(prob, eigenvector)
        vel = self.get_velocities(prob, eigenvector)
        thr = self.get_throughput(prob, eigenvector)
        return (vel_jump_dx/vel_jump), vel, (vel_jump_dx/vel_jump)/vel, thr
        #return vel
        #return (vel_jump_dx/vel_jump)/vel, vel_jump_dx, vel_jump, vel
        #return (vel_jump_dx/vel_jump)

    # ----------------------------------
    # Inna prędkość...
    # ----------------------------------    

    def get_throughput(self, prob, eigenvector):
        vels = []
        for polimer in eigenvector:
            vels.append(self.objects.get_or_create(polimer).throughput(prob) * eigenvector[polimer])
        return numpy.array(vels).sum(axis=0)

    def get_velocities(self, prob, eigenvector):
        return numpy.array([self.objects.get_or_create(polimer).get_velocity(prob) * eigenvector[polimer] for polimer in eigenvector]).sum(axis=0)

    # ----------------------------------
    # Inna prędkość...
    # ----------------------------------
    def get_velocities_jump_dx(self, prob, eigenvector):
        return sum([self.objects.get_or_create(polimer).get_velocity_jump_dx(prob) * eigenvector[polimer] for polimer in eigenvector])

    # ----------------------------------
    # Inna prędkość... z jumpem?
    # ----------------------------------
    def get_velocities_jump(self, prob, eigenvector):
        return sum([self.objects.get_or_create(polimer).get_velocity_jump(prob) * eigenvector[polimer] for polimer in eigenvector])
    # ----------------------------------
