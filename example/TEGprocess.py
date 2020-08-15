# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 11:07:21 2020

@author: ESOL
"""

from neqsim.process import openprocess


# Read dehydration process from file
#offshorePro = openprocess('c:/temp/offshorePro.neqsim')
TEGprocess = openprocess('../lib/TEGprocess.neqsim')
#TEGprocess.setFluid(TEGprocess.getUnit("dry feed gas").getFluid(), offshorePro.getUnit("richgas").getFluid())


# Set input parameters
TEGprocess.getUnit("dry feed gas").setTemperature(30.2, 'C')
TEGprocess.getUnit("dry feed gas").setPressure(52.21, "bara")
TEGprocess.getUnit("lean TEG to absorber").setFlowRate(6100.0, "kg/hr")
TEGprocess.getUnit("lean TEG cooler").setOutTemperature(273.15 + 44.85)
TEGprocess.getUnit("rich TEG preheater").setOutTemperature(273.15 + 38.5)
TEGprocess.getUnit("Rich TEG HP flash valve").setOutletPressure(4.9)
TEGprocess.getUnit("rich TEG heater HP").setOutTemperature(273.15 + 62.0)
TEGprocess.getUnit("LP rich glycol heater").setOutTemperature(273.15 + 139.0)
TEGprocess.getUnit("LP rich glycol heater").setOutPressure(1.23)
TEGprocess.getUnit("TEG regeneration column").getReboiler().setOutTemperature(273.15 + 206.6)
TEGprocess.getUnit("stripGas").setPressure(1.23, "bara")
TEGprocess.getUnit("stripGas").setFlowRate(61.88, "kg/hr")
TEGprocess.getUnit("stripGas").setTemperature(80.0, 'C')
TEGprocess.getUnit("lean TEG resycle").getOutletStream().setFlowRate(5500.0, "kg/hr")

#Run the process calculations
TEGprocess.run()


#Read results
wetGasRatekghr = TEGprocess.getUnit("water saturated feed gas").getFlowRate("kg/hr")
waterInWetGasppm = TEGprocess.getUnit("water saturated feed gas").getFluid().getPhase(0).getComponent('water').getz()*1.0e6
waterInDryGasppm = TEGprocess.getUnit("dry gas from absorber").getFluid().getPhase(0).getComponent('water').getz()*1.0e6
waterInWetGaskgMSm3 = waterInWetGasppm*0.01802*101325.0/(8.314*288.15)
waterInDryGaskgMSm3 = waterInDryGasppm*0.01802*101325.0/(8.314*288.15)
wtLeanTEGFromReboiler = TEGprocess.getUnit("TEG regeneration column").getLiquidOutStream().getFluid().getPhase("aqueous").getWtFrac("TEG")*100.0
wtLeanTEGFromStripper = TEGprocess.getUnit("TEG stripper").getSolventOutStream().getFluid().getPhase("aqueous").getWtFrac("TEG")*100.0
reboilerdutykW = TEGprocess.getUnit("TEG regeneration column").getReboiler().getDuty()/1.0e3
condenserdutykW = TEGprocess.getUnit("TEG regeneration column").getCondenser().getDuty()/1.0e3
glycolheaterdutykW = TEGprocess.getUnit("rich TEG preheater").getDuty()/1.0e3
condensertemperature= TEGprocess.getUnit("TEG regeneration column").getCondenser().getTemperature()-273.15
reboilertemperature= TEGprocess.getUnit("TEG regeneration column").getReboiler().getTemperature()-273.15
TEGmakeupkghr = TEGprocess.getUnit("gas to flare").getFluid().getPhase(0).getComponent("TEG").getFlowRate("kg/sec")*3600.0 + TEGprocess.getUnit("dry gas from absorber").getFluid().getPhase(0).getComponent("TEG").getFlowRate("kg/sec")*3600.0 + + TEGprocess.getUnit("gas from degasing separator").getFluid().getPhase(0).getComponent("TEG").getFlowRate("kg/sec")*3600.0
leanTEGflow = TEGprocess.getUnit("TEG absorber").getSolventInStream().getFlowRate("kg/hr")
richTEGflow = TEGprocess.getUnit("TEG absorber").getSolventOutStream().getFlowRate("kg/hr")
pump1DutykW = TEGprocess.getUnit("hot lean TEG pump").getEnergy()/1.0e3
pump2DutykW = TEGprocess.getUnit("lean TEG HP pump").getEnergy()/1.0e3
flashGasRate = TEGprocess.getUnit("gas from degasing separator").getFlowRate("kg/hr")
gasToFLareRatekghr = TEGprocess.getUnit("gas to flare").getFlowRate("kg/hr")






