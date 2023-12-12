# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 18:01:42 2020

@author: ESOL
"""


import neqsim
from neqsim.thermo.thermoTools import *
from neqsim.process import openprocess
from neqsim.process.processTools import simplereservoir
import tagreader
from tagreader.utils import ReaderType
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime
import numpy
import sys

dataOut = []
dataRes = []
for index, data in dfres.iterrows():
    dataloc = []
    TEGprocess.getUnit("dry feed gas").setFlowRate(data[1], 'MSm3/day')
    TEGprocess.getUnit("dry feed gas").setPressure(data[3], 'barg')
    TEGprocess.getUnit("dry feed gas").setTemperature(data[2], 'C')
    TEGprocess.getUnit("TP of gas to absorber").setOutTemperature(data[2], 'C')
    TEGprocess.getUnit("TP of gas to absorber").setOutPressure(data[3], "barg")
    TEGprocess.getUnit("lean TEG to absorber").setFlowRate(data[5]*1100.0, 'kg/hr')
    TEGprocess.getUnit("lean TEG cooler").setOutTemperature(273.15+data[12])
    TEGprocess.getUnit("Rich TEG HP flash valve").setOutletPressure(data[8], 'barg')
    TEGprocess.getUnit("Rich TEG LP flash valve").setOutletPressure(data[9], 'barg')
    TEGprocess.getUnit("filters").setDeltaP(data[15], "bara");
    TEGprocess.getUnit("TEG regeneration column").getCondenser().setOutTemperature(85.6+273.15)
    TEGprocess.getUnit("TEG regeneration column").getReboiler().setOutTemperature(data[11]+273.15)
    TEGprocess.getUnit("TEG regeneration column").setBottomPressure(data[9]+1.01325)
    TEGprocess.getUnit("TEG regeneration column").setTopPressure(data[9]+1.01325)
    TEGprocess.getUnit("TEG buffer tank").setOutTemperature(data[13]+273.15)
    TEGprocess.getUnit("hot lean TEG pump").setOutletPressure(data[14]+1.01325)
    TEGprocess.getUnit("rich TEG heat exchanger 1").setUAvalue(2900.0)
    TEGprocess.getUnit("rich TEG heat exchanger 2").setUAvalue(7300.0)
    if(data[1]<0.01):
        dataOut.append([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
        continue
    tic = time.perf_counter()
    try:
        neqsimthread = TEGprocess.runAsThread()
        neqsimthread.join()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)    
    except:
        print('error ', index)
        dataOut.append([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
        continue
    
    toc = time.perf_counter()
    print('time ', (toc-tic))
    
    dataloc.append(TEGprocess.getMeasurementDevice("hydrate temperature analyser").getMeasuredValue('C'))
    dataloc.append(TEGprocess.getUnit("feed to TEG absorber").getFluid().getPhase(0).getComponent('water').getz()*1.0e6*0.01802*101325.0/(8.314*288.15))
    dataloc.append(TEGprocess.getUnit("TEG regeneration column").getReboiler().getDuty()/1.0e3)
    dataloc.append(TEGprocess.getUnit("TEG regeneration column").getCondenser().getDuty()/1.0e3)
    dataloc.append(TEGprocess.getUnit("gas from degasing separator").getFlowRate("kg/hr"))
    dataloc.append(TEGprocess.getUnit("gas to flare").getFlowRate("kg/hr"))
    dataloc.append(TEGprocess.getUnit("hot lean TEG pump").getEnergy()/1.0e3)
    dataloc.append(TEGprocess.getUnit("lean TEG HP pump").getEnergy()/1.0e3)
    dataloc.append(TEGprocess.getUnit("TEG stripper").getSolventOutStream().getFluid().getPhase("aqueous").getWtFrac("TEG")*100.0)
    dataloc.append(TEGprocess.getUnit("filters").getDeltaP())
    dataloc.append(TEGprocess.getUnit("dry gas from absorber").getFluid().getPhase(0).getComponent('water').getz()*1.0e6)
    dataloc.append(TEGprocess.getMeasurementDevice("water dew point analyser").getMeasuredValue('C'))
    dataloc.append(TEGprocess.getMeasurementDevice("water dew point analyser2").getMeasuredValue('C'))
    
    #Condition monitor HX2
    conditionMonitor = TEGprocess.getConditionMonitor()
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 2").getInStream(0).setTemperature(data[16], "C")#TEGprocess.getUnit("rich TEG heat exchanger 2").getInStream(0).getTemperature("C"), "C")
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 2").getInStream(1).setTemperature(data[13], "C")
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 2").getOutStream(0).setTemperature(data[17], "C")#TEGprocess.getUnit("rich TEG heat exchanger 2").getOutStream(0).getTemperature("C"), "C")
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 2").getOutStream(1).setTemperature(data[19], "C")#TEGprocess.getUnit("rich TEG heat exchanger 2").getOutStream(1).getTemperature("C")+1, "C")
    conditionMonitor.conditionAnalysis("rich TEG heat exchanger 2")
    
    eff1 = conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 2").getThermalEffectiveness()
    eff2 = TEGprocess.getUnit("rich TEG heat exchanger 2").getThermalEffectiveness()
    relativeEfficiency = eff1/eff2
    dataloc.append(eff1)
    dataloc.append(eff2)
    dataloc.append(relativeEfficiency)
    print('effHX2_real ', eff1, ' effHX2_ref ', eff2, ' releffHX2 ', relativeEfficiency)
    
    leanTEGtempIntoHX2 = data[13]  # GFA.24-TIT__396_.PV   surge drup =
    leanTEGoutHX2 = TEGprocess.getUnit("rich TEG heat exchanger 2").getOutStream(1).getTemperature("C")   # TI374
    richTEGintoHx2  = TEGprocess.getUnit("rich TEG heat exchanger 2").getInStream(0).getTemperature("C")  # TI368    
    richTEGfromHc2toreboil =  TEGprocess.getUnit("rich TEG heat exchanger 2").getOutStream(0).getTemperature("C")  # TI370
    #dataOut.append([richTEGintoHx2, richTEGfromHc2toreboil, leanTEGtempIntoHX2, leanTEGoutHX2])
    
    
    
    
    #Condition monitor HX1
    conditionMonitor = TEGprocess.getConditionMonitor()
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 1").getInStream(0).setTemperature(data[20], "C")#TEGprocess.getUnit("rich TEG preheater").getOutStream().getTemperature("C"), "C")
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 1").getInStream(1).setTemperature(data[22], "C")#TEGprocess.getUnit("rich TEG heat exchanger 2").getOutStream(1).getTemperature("C"), "C")
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 1").getOutStream(0).setTemperature(data[21], "C")#TEGprocess.getUnit("rich TEG heat exchanger 1").getOutStream(0).getTemperature("C"), "C")
    conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 1").getOutStream(1).setTemperature(data[23], "C")#TEGprocess.getUnit("rich TEG heat exchanger 1").getOutStream(1).getTemperature("C"), "C")
    conditionMonitor.conditionAnalysis("rich TEG heat exchanger 1")
    
    eff11 = conditionMonitor.getProcess().getUnit("rich TEG heat exchanger 1").getThermalEffectiveness()
    eff21 = TEGprocess.getUnit("rich TEG heat exchanger 1").getThermalEffectiveness()
    relativeEfficiency1 = eff11/eff21
    dataloc.append(eff11)
    dataloc.append(eff21)
    dataloc.append(relativeEfficiency1)
    
    print('effHX1_real ', eff11, ' effHX1_ref ', eff21, ' releffHX1 ', relativeEfficiency1)
    
    leanTEGtempIntoHX1 = TEGprocess.getUnit("rich TEG preheater").getOutStream().getTemperature("C")
    leanTEGoutHX1 = TEGprocess.getUnit("rich TEG heat exchanger 1").getOutStream(0).getTemperature("C")
    richTEGintoHx1  = TEGprocess.getUnit("rich TEG heat exchanger 2").getOutStream(1).getTemperature("C")   
    richTEG1 =  TEGprocess.getUnit("rich TEG heat exchanger 1").getOutStream(1).getTemperature("C")
    #dataOut.append([leanTEGtempIntoHX1, leanTEGoutHX1, richTEGintoHx1, richTEG1])
    
    dataOut.append([richTEGintoHx2, richTEGfromHc2toreboil, leanTEGtempIntoHX2, leanTEGoutHX2, leanTEGtempIntoHX1, leanTEGoutHX1, richTEGintoHx1, richTEG1])
    
    #Condition monitor fine filter
    conditionMonitor = TEGprocess.getConditionMonitor()
    conditionMonitor.conditionAnalysis("filters")
    cvFactor = conditionMonitor.getProcess().getUnit("filters").getCvFactor()
    dataloc.append(cvFactor)
    dataRes.append(dataloc)
    print('Cv factor ', cvFactor)
    
    #dataOut.append([relativeEfficiency, relativeEfficiency1, cvFactor])
    
    
#plt.show()

a = numpy.asarray(dataOut)
numpy.savetxt("c:/temp/dataResults6.csv", a, delimiter=",")