"""
Oil process module
...
The module is sed for establishing a Oil process, 
setting input parameters and reading output from a simulation
"""
from functools import cache
from neqsim import jNeqSim
from pydantic.dataclasses import dataclass
from pydantic import Field
from neqsim.process import compressor, cooler, separator3phase, getProcess, clearProcess, mixer, heater, stream, pump, separator, runProcess, stream, saturator, valve, filters, heatExchanger, simpleTEGAbsorber,distillationColumn, waterStripperColumn, recycle2, setpoint, calculator
from neqsim.thermo import fluid, printFrame
from neqsim.thermo.thermoTools import readEclipseFluid, TPflash

@dataclass
class ProcessInput():
    """
    A class to define input parameters for the TEG dehydration process.

    ...

    Attributes
    ----------
    feedGasFlowRate : float
        the flow rate of the feed gas to the dehdyration process in unit MSm3/day
    flowrateTEG : float
        the flow rate of lean TEG to the dehdyration process in unit kg/hr
    """
    feedGasFlowRateHP: float = Field(
        11.65, ge=0.0, le=100.0, title="HP Feed gas flow rate (not saturated) [MSm3/day]")
    feedGasFlowRateLP: float = Field(
        5.65, ge=0.0, le=100.0, title="LP Feed gas flow rate (not saturated) [MSm3/day]")


@dataclass
class ProcessOutput():
    """
    A class to define output results from a Oil process simulation.

    ...

    Attributes
    ----------
    feedGasFlowRateHP : float
        the flow rate of well stream to process (MSm3/day)
    """
    feedGasFlowRateHP: float | None = None


@cache
def getprocess():
    """
    The method creates a oil process object using neqsim
    """
    inputdata = {
        'feedFlowRateHP': 10,
        'feedFlowRateLP': 3,
        'firstStagePressure': 60.0,
        'firstStageTemperature': 70.0,
        'secondStagePressure': 30.0,
        'secondStageTemperature': 80.0,
        'thirdStagePressure': 1.8,
        'thirdStageTemperature': 64.0,
        'export_oil_temperature': 55.0,
        'export_oil_pressure': 8.8,
        'firstStageRecompressorPressure': 6.5,

        'temperatureOilHeater' : 75.9,
        'secondStagePressure': 8.6,
        'thirdStagePressure': 1.9,
        'firstStageSuctionCoolerTemperature': 30.0, 
        'secondStageSuctionCoolerTemperature': 30.0, 
        'thirdStageSuctionCoolerTemperature':30.0,
        'firstStageExportCoolerTemperature': 30.0, 
        'secondStageExportCoolerTemperature': 30.0
    }
    clearProcess()

    wellFluid = readEclipseFluid('/workspaces/neqsimprocess/neqsimprocess/fluid1_E300.txt')
    #wellFluid.setMolarComposition([0.08, 3.56, 67.36, 8.02, 1.54, 0.2, 0.42, 0.15, 0.2, 1.24, 2.34, 1.33, 1.19, 1.15, 6.69, 5.5, 5.03])
 
    LPwellFLuid = wellFluid.clone()
    #LPwellFLuid.setMolarComposition([0.08, 3.56, 67.36, 8.02, 1.54, 0.2, 0.42, 0.15, 0.2, 1.24, 2.34, 1.33, 1.19, 1.15, 6.69, 5.5, 5.03])
 
    wellStreamHP = stream(wellFluid)
    wellStreamHP.setName("HP well stream")
    wellStreamHP.setFlowRate(ProcessInput.feedGasFlowRateHP, "MSm3/day")
    wellStreamHP.setTemperature(inputdata['firstStageTemperature'], "C")
    wellStreamHP.setPressure(inputdata['firstStagePressure'], "bara")

    LPwellStream = stream(wellFluid)
    LPwellStream.setName("LP well stream")
    LPwellStream.setFlowRate(ProcessInput.feedGasFlowRateLP, "MSm3/day")
    LPwellStream.setTemperature(inputdata['secondStageTemperature'], "C")
    LPwellStream.setPressure(inputdata['secondStagePressure'], "bara")

    firstStageSeparator = separator3phase(wellStreamHP)
    firstStageSeparator.setName("1st stage separator")

    oilHeaterFromFirstStage = heater(firstStageSeparator.getOilOutStream())
    oilHeaterFromFirstStage.setName("oil heater second stage")
    oilHeaterFromFirstStage.setOutTemperature(inputdata['secondStageTemperature'],'C')
    oilHeaterFromFirstStage.setOutPressure(inputdata['secondStagePressure'],'bara')

    secondStageSeparator = separator3phase(oilHeaterFromFirstStage.getOutStream())
    secondStageSeparator.addStream(LPwellStream)
    secondStageSeparator.setName("2nd stage separator")

    oilHeaterFromSecondStage = heater(firstStageSeparator.getOilOutStream())
    oilHeaterFromSecondStage.setName("oil heater third stage")
    oilHeaterFromSecondStage.setOutTemperature(inputdata['thirdStageTemperature'],'C')
    oilHeaterFromSecondStage.setOutPressure(inputdata['thirdStagePressure'],'bara')

    thirdStageSeparator = separator3phase(oilHeaterFromSecondStage.getOutStream())
    thirdStageSeparator.setName("3rd stage separator")

    oilThirdStageToSep =  wellStreamHP.clone()
    oilThirdStageToSep.setName("resyc oil")
    oilThirdStageToSep.setFlowRate(10.0, 'kg/hr')
    thirdStageSeparator.addStream(oilThirdStageToSep)

    exportoil = heater(thirdStageSeparator.getOilOutStream())
    exportoil.setName("export oil")
    exportoil.setOutTemperature(inputdata['export_oil_temperature'],'C')
    exportoil.setOutPressure(inputdata['export_oil_pressure'],'bara')

    firstStageCooler = cooler(thirdStageSeparator.getGasOutStream())
    firstStageCooler.setName("1st stage cooler")
    firstStageCooler.setOutTemperature(inputdata['firstStageSuctionCoolerTemperature'],'C')

    firstStageScrubber = separator(firstStageCooler.getOutStream())
    firstStageScrubber.setName("1st stage scrubber")

    firstStageCompressor = compressor(firstStageScrubber.getGasOutStream())
    firstStageCompressor.setName("1st stage compressor")
    firstStageCompressor.setOutletPressure(inputdata['firstStageRecompressorPressure'])
    firstStageCompressor.setIsentropicEfficiency(0.75)

    firstStageCooler2 = cooler(firstStageCompressor.getOutStream())
    firstStageCooler2.setName("1st stage cooler2")
    firstStageCooler2.setOutTemperature(inputdata['firstStageSuctionCoolerTemperature'],'C')

    firstStageScrubber2 = separator(firstStageCooler2.getOutStream())
    firstStageScrubber2.setName("1st stage scrubber2")

    firstStageCompressor2 = compressor(firstStageScrubber2.getGasOutStream())
    firstStageCompressor2.setName("1st stage compressor2")
    firstStageCompressor2.setOutletPressure(inputdata['secondStagePressure'])
    firstStageCompressor2.setIsentropicEfficiency(0.75)

    secondstagegasmixer = mixer("second Stage mixer")
    secondstagegasmixer.addStream(firstStageCompressor2.getOutStream())
    secondstagegasmixer.addStream(secondStageSeparator.getGasOutStream())

    secondStageCooler = cooler(secondstagegasmixer.getOutStream())
    secondStageCooler.setName("2nd stage cooler")
    secondStageCooler.setOutTemperature(inputdata['secondStageSuctionCoolerTemperature'],'C')

    secondStageScrubber = separator(secondStageCooler.getOutStream())
    secondStageScrubber.setName("2nd stage scrubber")

    secondStageCompressor = compressor(secondStageScrubber.getGasOutStream())
    secondStageCompressor.setName("2nd stage compressor")
    secondStageCompressor.setOutletPressure(inputdata['firstStagePressure'])
    secondStageCompressor.setIsentropicEfficiency(0.75)

    richGasMixer = mixer("fourth Stage mixer")
    richGasMixer.addStream(secondStageCompressor.getOutStream())
    richGasMixer.addStream(firstStageSeparator.getGasOutStream())

    dewPointControlCooler = cooler(richGasMixer.getOutStream())
    dewPointControlCooler.setName("dew point cooler")
    dewPointControlCooler.setOutTemperature(inputdata['thirdStageSuctionCoolerTemperature'],'C')

    dewPointScrubber = separator(dewPointControlCooler.getOutStream())
    dewPointScrubber.setName("dew point scrubber")

    lpLiqmixer = mixer("LP liq gas mixer");
    lpLiqmixer.addStream(firstStageScrubber.getLiquidOutStream());
    lpLiqmixer.addStream(firstStageScrubber2.getLiquidOutStream());
    lpLiqmixer.addStream(secondStageScrubber.getLiquidOutStream());
    lpLiqmixer.addStream(dewPointScrubber.getLiquidOutStream());
    
    lpResycle = recycle2("LP liq resycle")
    lpResycle.addStream(lpLiqmixer.getOutStream())
    lpResycle.setOutletStream(oilThirdStageToSep)

    exportCompressor1 = compressor(dewPointScrubber.getGasOutStream())
    exportCompressor1.setName("export 1st stage")
    exportCompressor1.setOutletPressure(140.0)
    exportCompressor1.setIsentropicEfficiency(0.75)

    exportInterstageCooler = cooler(exportCompressor1.getOutStream())
    exportInterstageCooler.setName("interstage stage cooler")
    exportInterstageCooler.setOutTemperature(inputdata['firstStageExportCoolerTemperature'],'C')

    exportCompressor2= compressor(exportInterstageCooler.getOutStream())
    exportCompressor2.setName("export 2nd stage")
    exportCompressor2.setOutletPressure(200.0)
    exportCompressor2.setIsentropicEfficiency(0.75)

    exportCooler = cooler(exportCompressor1.getOutStream())
    exportCooler.setName("export cooler")
    exportCooler.setOutTemperature(inputdata['secondStageExportCoolerTemperature'],'C')

    exportGas = stream(exportCooler.getOutStream())
    exportGas.setName("export gas")

    oilprocess = getProcess()
    return oilprocess


def updateinput(process, locinput):
    """
    update process with input parameters
    """
    process.getUnit('HP well stream').setFlowRate(
        locinput.feedGasFlowRateHP, 'MSm3/day')


def getoutput():
    # update output
    outputparam = {
        'feedGasFlowRateHP': oilprocess.getUnit('HP well stream').getFluid().getComponent(0).getx()*1e6,
    }
    return outputparam


if __name__ == "__main__":
    # Test running the oil process

    # Read input
    inputparam = {
        'feedGasFlowRateHP': 11.65
    }

    # Create TEG process
    oilprocess = getprocess()

    # update input in model
    updateinput(process=oilprocess, locinput=ProcessInput(**inputparam))

    # run calculation
    thread = oilprocess.runAsThread()
    thread.join(5*60*1000)

    if thread.isAlive():
        thread.stop()
        raise Exception(
            f"Oilgas process calculation did not converge within 5 minutes"
        )

    # read and print results
    results = ProcessOutput(**getoutput())
    print(results.__dict__)
