# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 21:36:01 2020

@author: ESOL
"""


from neqsim.process import openprocess
import time

onshoreMEG = openprocess('c:/temp/onshoreMEGprocess.neqsim')


onshoreMEG.getUnit("dry feed gas").setFlowRate(10.5, "MSm3/day")
onshoreMEG.getUnit("dry feed gas").setTemperature(6.0, "C")
onshoreMEG.getUnit("dry feed gas").setPressure(53.0, "bara")
onshoreMEG.getUnit("2nd stage compressor").setOutletPressure(105.0, "bara")
onshoreMEG.getUnit("lean MEG for distribution").setFlowRate(1100.0, "kg/hr")
onshoreMEG.getUnit("inlet gas cooler").setOutTemperature(10.0, "C")
onshoreMEG.getUnit("low temperature JT valve").setOutletPressure(92.0, "bara")
onshoreMEG.getUnit("LP pressure reduction valve").setOutletPressure(7.0, "bara")
onshoreMEG.getUnit("MEG regeneration column").getCondenser().setOutTemperature(273.15+110.0)
onshoreMEG.getUnit("MEG regeneration column").getReboiler().setOutTemperature(273.15+135.0)

tic = time.perf_counter()
onshoreMEG.run()
toc = time.perf_counter()
print(f"Simulation run in {toc - tic:0.4f} seconds")

wetGasFLow = onshoreMEG.getUnit("water saturated feed gas").getFlowRate("MSm3/day")
reboilerdutykW = onshoreMEG.getUnit("MEG regeneration column").getReboiler().getDuty()/1.0e3
lowTsepTemperature = onshoreMEG.getUnit("rich MEG stream").getTemperature("C")
wtprleanMEG = onshoreMEG.getUnit("MEG regeneration column").getLiquidOutStream().getFluid().getPhase("aqueous").getWtFrac("MEG")*100
richTEGwt = onshoreMEG.getUnit("rich MEG stream").getFluid().getPhase("aqueous").getWtFrac("MEG")*100
ppmWaterInDFeedGas = onshoreMEG.getUnit("water saturated feed gas").getFluid().getPhase("gas").getComponent("water").getx()*1e6
ppmWaterInDryGas = onshoreMEG.getUnit("gas from cold sep").getFluid().getPhase("gas").getComponent("water").getx()*1e6
gasToVentkghr  = onshoreMEG.getUnit("gas to flare").getFlowRate("kg/hr")
waterToSea  = onshoreMEG.getUnit("water to sea").getFlowRate("kg/hr")
MEGmakeupkghr  = onshoreMEG.getUnit("makeup MEG").getFlowRate("kg/hr")


totalPower = onshoreMEG.getPower('')/1.0e6
totalCoolingDuty = onshoreMEG.getCoolerDuty('')/1.0e6
totalHeatingDuty = onshoreMEG.getHeaterDuty('')/1.0e6