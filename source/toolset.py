#!/usr/bin/env python
# -*- coding: UTF8 -*-
#
#   NEURON miniproject, for the course "Neural networks and
#   biological modelling" 
#
#   This file contains model definitions (neurons) and helper functions (such
#   as I Clamp tests and visualisation functions)
#
#   AUTHOR: Douglas Watson <douglas@watsons.ch>
#
#   DATE: started on 14th April 2011
#
#   LICENSE: GNU GPL
#
#################################################

import neuron
import nrn

import numpy as np
import matplotlib.pyplot as plt

# The HH_traub and IM_cortex models should be imported automatically.

# Set temperature
h = neuron.h
h.celsius = 36

##############################
# Model definitions
##############################

# Define a generic section class, that will be used to initalize the three
# models HH, HHx, and HHxx, then customised.

class DefaultSection(nrn.Section):

    """ Defines the default values for all the somas we will use """

    def __init__(self, name):
        nrn.Section.__init__(self)
        self.name = name

        self.L = 67        # set length to 67 um
        self.diam = 67     # same for diameter
        self.Ra = 100      # intracellular resistivity

        # Add passive membrane mechanism
        self.insert('pas')
        self(0.5).pas.g = 0.00015 # conductivity
        self(0.5).pas.e = -70.0   # reversal potential

        # And H-H model, with a sodium and potassium channel.
        self.insert('hh2')
        self.insert('k_ion')
        self.insert('na_ion')

        # And 40 alpha synapses equally distributed along the section:
        for i in range(40):
            # TODO check units
            syn = h.AlphaSynapse(i/40.0, sec=self)
            syn.tau = 2 # 2 ms
            syn.e = 0   # 0 mV reversal potential
            syn.gmax = 0.005 # uS


################################
# Testing and simulation control
################################

def run_IClamp(sec, pos=0.5, delay=0, dur=100, amp=10, dt=0.025, tstop=30, 
        v_init=-70):
    # TODO again, make sure integration units are actually seconds.
    """ 
    Simulate a current clamp measurement on section *sec*, stimulated by step
    current. Returns an array of (time, voltage) pairs.

    INPUT:

    Arguments for IClamp:
    sec - section (HH, HHx, ...)
    pos - position of electrode along section (typically 0.5)
    delay - delay before step in ms
    dur - duration of step in ms
    amp - amplitude of current in nA

    Arguments for simulation:
    dt - timestep in ms
    tstop - endtime in ms!
    v_init - initial membrane potential in mV

    """
    # Define stimulate HH in the middle.
    stim = h.IClamp(pos, sec=sec)
    stim.delay = delay
    stim.dur =  dur
    stim.amp = amp

    # Simulation control
    # TODO make sure units are actually seconds
    h.dt = dt
    h.finitialize(v_init)
    h.fcurrent()
    
    # Run simulation: integrate and record data
    data = np.array([])  # array of (time, voltage) points
    while h.t < tstop:
        h.fadvance()
        data = np.reshape(np.append(data, [h.t, sec(0.5).v]), (-1, 2))
    return data

################################
# Helper functions
################################

def spiketimes(data, v_th=0.5):
    """Given voltage and time, returns array of spike times

    Note: Code ripped off from one of the python exercise examples.

    INPUT:

    data - 2D array of [time, voltage] pairs

    """

    v, t = np.transpose(data)
    v_above_th = v>v_th
    idx = np.nonzero((v_above_th[:-1]==False)&(v_above_th[1:]==True))
    return t[idx[0]+1]

def spikefreq(data, v_th=0.5):
    """Given voltage and time, returns spiking frequency

    INPUT:

    data - 2D array of [time, voltage] pairs

    """
    times = spiketimes(data, v_th=0.5)
    if len(times) > 1:
        freq = mean(diff(times))
    else:
        freq = 0
    return freq

################################
# Visualisation
################################

def U_vs_t(data, linestyle='k-'):
    """ Returns a U vs t plot for data 
    
    INPUT
    
    data - an array of [t, v] pairs
    linestyle - matlab-style code for the linestyle
    """
    ax = plt.axes()
    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("Membrane potential [mV]")

    t, v = np.transpose(data)
    ax.plot(t, v, linestyle)
    ax.set_ylim(-80, 100)

    return ax

def f_vs_I(data, linestyle='k-', label=""):
    """ Returns plot of spiking frequency versus stimulation current
    
    INPUT
    
    data - a list of [I, clampdata] pairs, where clampdata is an array of [t,
    v] pairs.
    linestyle - matlab-style code for the linestyle
    
    """
    ax = plt.axes()
    ax.set_xlabel("Current [nA]")
    ax.set_ylabel("Spiking Frequency [kHz]")

    points = [[I, spikefreq(d)] for I, d in data]
    I, f = np.transpose(points)

    ax.plot(I, f, linestyle, label=label)

    return ax

if __name__ == '__main__':
    HH = DefaultSection("HH")
    # Run simulation and plot
    data = run_IClamp(sec=HH, delay=0, dur=20, amp=40, tstop=30)
    # ax = U_vs_t(data)

    # Type I or II?
    data = []
    for I in np.arange(5, 1000, 10):
        clampdata = run_IClamp(sec=HH, delay=0, dur=10, amp=I, tstop=30)
        data.append([I, clampdata])
    ax = f_vs_I(data, 'k.')
        
    plt.show()
