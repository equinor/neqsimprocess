from neqsim.process.processTools import (compsplitter, waterDewPointAnalyser, hydrateEquilibriumTemperatureAnalyser, virtualstream, clearProcess, newProcess, runProcess, stream, runProcessAsThread, mixer, compressor, recycle2, splitter, valve)
from neqsim.thermo import (TPflash, fluid, printFrame)
from numpy import isnan
from pytest import approx
from jpype.types import *


def test_Viscosity():
    assert abs(1.0760998263782569e-015) < 1e-10
    
def test_teg_process():
    