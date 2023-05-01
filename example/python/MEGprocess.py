# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 14:48:08 2020

@author: ESOL
"""

from neqsim.process import openprocess
import time

MEGwell = openprocess('c:/temp//MEGinjection.neqsim')

MEGwell.getUnit('feed fluid').setFlowRate(13.2, 'MSm3/day')
MEGwell.getUnit('gas-MEG pipeline').setOutTemperature(273.15 + 25.5)
MEGwell.getUnit('gas-MEG pipeline').setOutPressure(80.2)

MEGwell.run()

leanMEGflow = MEGwell.getUnit("lean MEG feed stream").getFlowRate("kg/hr")

MEGwell.getUnit('feed fluid').displayResult()