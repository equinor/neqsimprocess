# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:50:32 2020

@author: ESOL
"""

from neqsim import thermo
from neqsim import process
from neqsim.thermo import fluid, fluid_df, TPflash, printFrame
from neqsim.process import clearProcess, stream, runProcess, viewProcess, separator, saturator, glycoldehydrationlmodule
import pandas as pd

# The process is glycol process simualtion is done in three steps:
# 1. Create feed stream
# 2. Set up the process units
# 3. Input process conditions 
# 4. Run simulations
# 5. Read simulation results


#1.  Create the feed gas stream
naturalgas = {'ComponentName':  ["nitrogen", "CO2", "H2S", "methane", "ethane", "propane", "i-butane", "n-butane", "i-pentane", "n-pentane", "n-hexane","benzene", "n-heptane","toluene","n-octane","m-Xylene", "TEG", "water"], 
        'MolarComposition[-]':  [0.34, 0.84, 0.0001, 90.4, 5.199, 2.06, 0.36, 0.55, 0.14, 0.097, 0.014,0.008,0.01, 0.001, 0.001, 0.0001,0.0, 0.01]
} 

naturalgasdf = pd.DataFrame(naturalgas) 
naturalgasFluid = fluid_df(naturalgasdf)

#2. Setting up glycol process
clearProcess()

feedStream = stream(naturalgasFluid)

#Saturate the feed stream with water
watersaturator = saturator(feedStream)

#Add a glycol dehydration module
TEGprocess = glycoldehydrationlmodule(watersaturator.getOutStream())


# 3. Set process parameters
feedStream.setPressure(50.0, 'bara')
feedStream.setTemperature(30.0, 'C')
feedStream.setFlowRate(5.0, "MSm3/day")
TEGprocess.setProperty("water dew point", 273.15 - 18.0, "C")
TEGprocess.setSpecification("number of theoretical stages", 1.5)
#TEGprocess.setProperty("lean glycol flow", 15.5, "m3/hr")
TEGprocess.setProperty("flash drum pressure", 5.0, "bara")
TEGprocess.setProperty("regeneration pressure", 1.21325, "bara")
TEGprocess.setProperty("reboiler temperature", 273.15 + 205.0, "C")
TEGprocess.setProperty("stripping gas rate", 0.01, "MSm3/day")

# 4. Run simulation
runProcess()


# 5. Read results from process units
waterinfeedgas = feedStream.getFluid().getComponent('water').getz()
waterindrygas = TEGprocess.getUnit("dehydrated gas").getFluid().getComponent('water').getz()
drygastemperature = TEGprocess.getUnit("dehydrated gas").getTemperature('C')
reboilerduty = TEGprocess.getUnit("reboiler").getDuty("duty", "kW", "","")
drygasflow = TEGprocess.getUnit("dehydrated gas").getFlowRate('Sm3/day')
theoreticalabsorberStages = TEGprocess.getUnit("absorber").getNumberOfTheoreticalStages()

# 6. Update process parameters 
TEGprocess.getUnit("lean TEG to absorber").setFlowRate(10000.0, "kg/hr")
feedStream.setPressure(50.0, 'bara')
feedStream.setTemperature(30.0, 'C')
feedStream.setTotalFlowRate(5.0, "MSm^3/day")


# 7. Run simulation 
runProcess()

# 8. Read results from process units
waterinfeedgas = feedStream.getFluid().getComponent('water').getz()
waterindrygas = TEGprocess.getUnit("dehydrated gas").getFluid().getComponent('water').getz()


