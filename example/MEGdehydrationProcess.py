# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 11:07:21 2020

@author: ESOL
"""

from neqsim.process import openprocess
import time


MEGprocess = openprocess('c:/temp//MEGdehydrationProcess.neqsim')


# Set input parameters
MEGprocess.getUnit("feed gas").setFlowRate(10.5, 'MSm3/day')
MEGprocess.getUnit("feed gas").setTemperature(6.0, 'C')
MEGprocess.getUnit("feed gas").setPressure(53.0, "bara")

MEGprocess.getUnit("Compressor 1 - first stage").setOutletPressure(70.0, "bara")
MEGprocess.getUnit("Compressor 1 - second stage").setOutletPressure(105.0, "bara")

MEGprocess.getUnit("lean MEG to header").setFlowRate(1000.0, "kg/hr")

#Run the process calculations
tic = time.perf_counter()
MEGprocess.run()
toc = time.perf_counter()
print(f"Simulation run in {toc - tic:0.4f} seconds")

#Read results
wetGasRatekghr = MEGprocess.getUnit("water saturated feed gas").getFlowRate("kg/hr")
waterInWetGasppm = MEGprocess.getUnit("heated gas from cold scrubber").getFluid().getPhase(0).getComponent('water').getz()*1.0e6
waterInDryGasppm = MEGprocess.getUnit("water saturated feed gas").getFluid().getPhase(0).getComponent('water').getz()*1.0e6









