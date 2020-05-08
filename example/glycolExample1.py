# -*- coding: utf-8 -*-
"""
Created on Thu May  7 14:56:27 2020

@author: ESOL
"""

print('example of process condition monitor....')

from neqsim import thermo
from neqsim import process
from neqsim.thermo import fluid, fluid_df, TPflash, printFrame
from neqsim.process import clearProcess, stream, runProcess, viewProcess, separator, glycoldehydrationlmodule
import pandas as pd


#The process isglycol process simualtion is done in three steps:
#1. Create feed stream
#2. Set up the process units
#3. Run simulations and read results


#1.  Create the feed gas stream
naturalgas = {'ComponentName':  ["nitrogen", "CO2", "H2S", "methane", "ethane", "propane", "i-butane", "n-butane", "i-pentane", "n-pentane", "n-hexane","benzene", "n-heptane","toluene","n-octane","m-Xylene", "MEG", "water"], 
        'MolarComposition[-]':  [0.34, 0.84, 0.0001, 90.4, 5.199, 2.06, 0.36, 0.55, 0.14, 0.097, 0.014,0.008,0.01, 0.001, 0.001, 0.0001,0.0, 0.1]
} 

naturalgasdf = pd.DataFrame(naturalgas) 
naturalgasFluid = fluid_df(naturalgasdf)



#2. Setting up glycol process
clearProcess()
feedStream = stream(naturalgasFluid)
feedStream.setPressure(50.0, 'bara')
feedStream.setTemperatue(30.0, 'C')
#Adding gas scrubber
feedGasScrubber = separator(feedStream, "inlet gas scrubber")
# Adding glycol dehydration module
glycoldehydrationlmodule(feedGasScrubber.getGasOutSteam())



#3. Adding transmitters and controllers
feedTemperatureT = temperaturetransmitter(feedStream, name='TT2987', unit="C")
feedTemperatureController = controller(leanGlycolFlowRateT, 'TC2987')

feedGasFlowRateT = flowtransmitter(feedStream, 'FT2878', unit='kg/hr')
feedGasFlowRateController = controller(feedGasFlowRateT, 'FC2878')

leanGlycolFlowRateT = flowtransmitter(leanGlycolStream, 'FT9878', unit='kg/hr')
leanGlycolFlowRateController = controller(leanGlycolFlowRateT, 'FC9879')

reboilerDutuy = energytransmitter(reboiler, 'QE9878', unit='kW')


#4. set process conditions
getProcess().getController('TC2987').setControllerSetPoint(25.1)
getProcess().getController('FC2878').setControllerSetPoint(6032.0)
getProcess().getController('FC9879').setControllerSetPoint(1020.0)

#5. Run simulation and read results from tranmitters
runProcess()

#6. Read results back
resultdataframe = getProcess().getResultdf()

#loop back to 4.....


