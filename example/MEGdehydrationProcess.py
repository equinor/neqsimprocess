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
MEGprocess.getUnit("Compressor 1 - interstage cooler").setOutTemperature(40.0, "C")
MEGprocess.getUnit("Compressor 1 - second stage").setOutletPressure(105.0, "bara")
MEGprocess.getUnit("lean MEG to header").setFlowRate(1000.0, "kg/hr")
MEGprocess.getUnit("lean MEG to header").setTemperature(20.0, "C")
MEGprocess.getUnit("lean MEG to header").setPressure(105.0, "bara")
MEGprocess.getUnit("dehydration cooler").setOutTemperature(10.0, "C")
MEGprocess.getUnit("gas-gas heat exchanger").setUAvalue(30000.0)
MEGprocess.getUnit("JT valve").setOutletPressure(92.0)
MEGprocess.getUnit("rich MEG pre-heater").setOutTemperature(15.0, "C")
MEGprocess.getUnit("valve to flash drum").setOutletPressure(10.0)
MEGprocess.getUnit("MEG/MEG heat exchanger").setUAvalue(500.0)
MEGprocess.getUnit("valve to regenerator").setOutletPressure(1.23)
MEGprocess.getUnit("MEG regeneration column").getReboiler().setOutTemperature(273.15 + 135.0)
MEGprocess.getUnit("MEG regeneration column").getCondenser().setOutTemperature(273.15 + 105.0)
MEGprocess.getUnit("regeneration overhead  gas cooler").setOutTemperature(273.15 + 20.0)
MEGprocess.getUnit("MEG buffer tank").setOutTemperature(273.15+130.0)
MEGprocess.getUnit("hot lean MEG pump").setOutletPressure(20.0)
MEGprocess.getUnit("hot lean MEG pump").setIsentropicEfficiency(0.75)
MEGprocess.getUnit("lean MEG HP pump").setOutletPressure(105.0)
MEGprocess.getUnit("lean MEG HP pump").setIsentropicEfficiency(0.75)
MEGprocess.getUnit("lean MEG cooler").setOutTemperature(273.15 + 20.0)

#Run the process calculations
tic = time.perf_counter()
MEGprocess.run()
toc = time.perf_counter()
print(f"Simulation run in {toc - tic:0.4f} seconds")

#Read results
wetGasRatekghr = MEGprocess.getUnit("water saturated feed gas").getFlowRate("kg/hr")
waterInWetGasppm = MEGprocess.getUnit("heated gas from cold scrubber").getFluid().getPhase(0).getComponent('water').getz()*1.0e6
waterInDryGasppm = MEGprocess.getUnit("water saturated feed gas").getFluid().getPhase(0).getComponent('water').getz()*1.0e6









