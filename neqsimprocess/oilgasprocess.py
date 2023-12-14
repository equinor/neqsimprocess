"""
Oil process module
...
The module is used for establishing an Oil process, 
setting input parameters and reading output from a simulation
"""
from functools import cache
from neqsim import jNeqSim
from pydantic.dataclasses import dataclass
from pydantic import Field
from neqsim.process import compressor, cooler, separator3phase, getProcess, clearProcess, mixer, heater, stream, pump, separator, runProcess, stream, valve, recycle2
from neqsim.thermo import fluid
from neqsim.thermo.thermoTools import readEclipseFluid

@dataclass
class ProcessInput():
    """
    A class to define input parameters for the oil process.

    ...

    Attributes
    ----------
    feedGasFlowRateHP : float
        HP wells flow rate in unit MSm3/day
    feedGasFlowRateLP : float
        LP wells flow rate in unit MSm3/day
    """
    feedGasFlowRateHP: float = Field(
        10.0, ge=0.0, le=100.0, title="HP Feed gas flow rate (not saturated) [MSm3/day]")
    feedGasFlowRateLP: float = Field(
        5.6, ge=0.0, le=100.0, title="LP Feed gas flow rate (not saturated) [MSm3/day]")
    firstStagePressure: float = Field(
        60.0, ge=0.0, le=100.0, title="Pressure of first stage separator [bara]")
    firstStageTemperature: float = Field(
        70.0, ge=0.0, le=100.0, title="Temperature of first stage separator [C]")
    secondStagePressure: float = Field(
        30.0, ge=0.0, le=100.0, title="Second stage separator pressure [bara]")
    secondStageTemperature: float = Field(
        80.0, ge=0.0, le=100.0, title="Second stage separator temperature [C]")
    thirdStagePressure: float = Field(
        1.8, ge=0.0, le=100.0, title="Third stage separator pressure [bara]")
    thirdStageTemperature: float = Field(
        64.0, ge=0.0, le=100.0, title="Third stage separator temperature [C]")
    export_oil_temperature: float = Field(
        55.0, ge=0.0, le=100.0, title="export oil temperature [C]")
    export_oil_pressure: float = Field(
        8.8, ge=0.0, le=100.0, title="export oil pressure [bara]")
    firstStageRecompressorPressure: float = Field(
        6.5, ge=0.0, le=100.0, title="First stage recompression pressure [bara]")
    dew_point_scrubber_temperature: float = Field(
        30.0, ge=0.0, le=100.0, title="Dew point scrubber temperature [C]")
    export_gas_pressure: float = Field(
        130.0, ge=0.0, le=200.0, title="Export gas pressure [bara]")
    export_gas_temperature: float = Field(
        55.0, ge=0.0, le=100.0, title="Export gas temperature [C]")
    suctionCoolerTemperature: float = Field(
        30.0, ge=0.0, le=100.0, title="Compressor after cooler temperatures [C]")

@dataclass
class ProcessOutput():
    """
    A class to define output results from a Oil process simulation.

    ...

    Attributes
    ----------
    mass_balance _ float
        check of mass balance for simulation
    recompressor1_power : float
        power of first stage compressor (kW)
    recompressor2_power : float
        power of second stage compressor (kW)
    recompressor3_power : float
        power of third stage compressor (kW)
    exportcompressor_power : float
        power of export compressor (kW)
    gasexportflow : float
        gasexportflow (MSm3/day)
    oilexportflow : float
        oilexportflow (m3/hr)
    """
    mass_balance: float | None = None
    recompressor1_power: float | None = None
    recompressor2_power: float | None = None
    recompressor3_power: float | None = None
    exportcompressor_power: float | None = None
    gasexportflow: float | None = None
    oilexportflow: float | None = None
    



@cache
def getprocess():
    """
    The method creates a oil process object using neqsim
    """
    clearProcess()

    wellFluid = readEclipseFluid('/workspaces/neqsimprocess/neqsimprocess/fluid1_E300.txt')
    #wellFluid.setMolarFlowRates([0.08, 3.56, 67.36, 8.02, 1.54, 0.2, 0.42, 0.15, 0.2, 1.24, 2.34, 1.33, 1.19, 1.15, 6.69, 5.5, 5.03])
 
    LPwellFLuid = wellFluid.clone()
    #LPwellFLuid.setMolarFlowRates([0.08, 3.56, 67.36, 8.02, 1.54, 0.2, 0.42, 0.15, 0.2, 1.24, 2.34, 1.33, 1.19, 1.15, 6.69, 5.5, 5.03])
 
    wellStreamHP = stream(wellFluid)
    wellStreamHP.setName("HP well stream")
    wellStreamHP.setFlowRate(ProcessInput.feedGasFlowRateHP, "MSm3/day")
    wellStreamHP.setTemperature(ProcessInput.firstStageTemperature, "C")
    wellStreamHP.setPressure(ProcessInput.firstStagePressure, "bara")

    LPwellStream = stream(LPwellFLuid)
    LPwellStream.setName("LP well stream")
    LPwellStream.setFlowRate(ProcessInput.feedGasFlowRateLP, "MSm3/day")
    LPwellStream.setTemperature(ProcessInput.secondStageTemperature, "C")
    LPwellStream.setPressure(ProcessInput.secondStagePressure, "bara")

    firstStageSeparator = separator3phase(wellStreamHP)
    firstStageSeparator.setName("1st stage separator")

    oilHeaterFromFirstStage = heater(firstStageSeparator.getOilOutStream())
    oilHeaterFromFirstStage.setName("oil heater second stage")
    oilHeaterFromFirstStage.setOutTemperature(ProcessInput.secondStageTemperature,'C')
    oilHeaterFromFirstStage.setOutPressure(ProcessInput.secondStagePressure,'bara')

    secondStageSeparator = separator3phase(oilHeaterFromFirstStage.getOutStream())
    secondStageSeparator.addStream(LPwellStream)
    secondStageSeparator.setName("2nd stage separator")

    oilHeaterFromSecondStage = heater(secondStageSeparator.getOilOutStream())
    oilHeaterFromSecondStage.setName("oil heater third stage")
    oilHeaterFromSecondStage.setOutTemperature(ProcessInput.thirdStageTemperature,'C')
    oilHeaterFromSecondStage.setOutPressure(ProcessInput.thirdStagePressure,'bara')

    thirdStageSeparator = separator3phase(oilHeaterFromSecondStage.getOutStream())
    thirdStageSeparator.setName("3rd stage separator")

    oilThirdStageToSep =  wellStreamHP.clone()
    oilThirdStageToSep.setName("resyc oil")
    oilThirdStageToSep.setFlowRate(10.0, 'kg/hr')
    thirdStageSeparator.addStream(oilThirdStageToSep)

    exportoil = heater(thirdStageSeparator.getOilOutStream())
    exportoil.setName("export oil cooler")
    exportoil.setOutTemperature(ProcessInput.export_oil_temperature,'C')
    exportoil.setOutPressure(ProcessInput.export_oil_pressure,'bara')

    exportoilstream = stream(exportoil.getOutStream())
    exportoilstream.setName('export oil')

    firstStageCooler = cooler(thirdStageSeparator.getGasOutStream())
    firstStageCooler.setName("1st stage cooler")
    firstStageCooler.setOutTemperature(ProcessInput.suctionCoolerTemperature,'C')

    firstStageScrubber = separator(firstStageCooler.getOutStream())
    firstStageScrubber.setName("1st stage scrubber")

    firstStageCompressor = compressor(firstStageScrubber.getGasOutStream())
    firstStageCompressor.setName("1st stage compressor")
    firstStageCompressor.setOutletPressure(ProcessInput.firstStageRecompressorPressure)
    firstStageCompressor.setIsentropicEfficiency(0.75)

    firstStageCooler2 = cooler(firstStageCompressor.getOutStream())
    firstStageCooler2.setName("1st stage cooler2")
    firstStageCooler2.setOutTemperature(ProcessInput.suctionCoolerTemperature,'C')

    firstStageScrubber2 = separator(firstStageCooler2.getOutStream())
    firstStageScrubber2.setName("1st stage scrubber2")

    firstStageCompressor2 = compressor(firstStageScrubber2.getGasOutStream())
    firstStageCompressor2.setName("2nd stage compressor")
    firstStageCompressor2.setOutletPressure(ProcessInput.secondStagePressure)
    firstStageCompressor2.setIsentropicEfficiency(0.75)

    secondstagegasmixer = mixer("second Stage mixer")
    secondstagegasmixer.addStream(firstStageCompressor2.getOutStream())
    secondstagegasmixer.addStream(secondStageSeparator.getGasOutStream())

    secondStageCooler = cooler(secondstagegasmixer.getOutStream())
    secondStageCooler.setName("2nd stage cooler")
    secondStageCooler.setOutTemperature(ProcessInput.suctionCoolerTemperature,'C')

    secondStageScrubber = separator(secondStageCooler.getOutStream())
    secondStageScrubber.setName("2nd stage scrubber")

    secondStageCompressor = compressor(secondStageScrubber.getGasOutStream())
    secondStageCompressor.setName("3rd stage compressor")
    secondStageCompressor.setOutletPressure(ProcessInput.firstStagePressure)
    secondStageCompressor.setIsentropicEfficiency(0.75)

    richGasMixer = mixer("fourth Stage mixer")
    richGasMixer.addStream(secondStageCompressor.getOutStream())
    richGasMixer.addStream(firstStageSeparator.getGasOutStream())

    dewPointControlCooler = cooler(richGasMixer.getOutStream())
    dewPointControlCooler.setName("dew point cooler")
    dewPointControlCooler.setOutTemperature(ProcessInput.dew_point_scrubber_temperature,'C')

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
    lpResycle.setTolerance(1e-6)

    exportCompressor1 = compressor(dewPointScrubber.getGasOutStream())
    exportCompressor1.setName("export gas compressor")
    exportCompressor1.setOutletPressure(ProcessInput.export_gas_pressure, 'bara')
    exportCompressor1.setIsentropicEfficiency(0.75)

    exportGasCooler = cooler(exportCompressor1.getOutStream())
    exportGasCooler.setName("export gas cooler")
    exportGasCooler.setOutTemperature(ProcessInput.export_gas_temperature,'C')

    exportGas = stream(exportGasCooler.getOutStream())
    exportGas.setName("export gas")

    oilprocess = getProcess()
    return oilprocess


def updateinput(process, locinput):
    """
    update process with input parameters
    """
    process.getUnit('HP well stream').setFlowRate(locinput.feedGasFlowRateHP, 'MSm3/day')
    process.getUnit('HP well stream').setTemperature(locinput.firstStageTemperature, "C")
    process.getUnit('HP well stream').setPressure(locinput.firstStagePressure, "bara")
    process.getUnit('LP well stream').setFlowRate(ProcessInput.feedGasFlowRateLP, "MSm3/day")
    process.getUnit('LP well stream').setTemperature(ProcessInput.secondStageTemperature, "C")
    process.getUnit('LP well stream').setPressure(ProcessInput.secondStagePressure, "bara")
    process.getUnit('oil heater second stage').setOutTemperature(ProcessInput.secondStageTemperature,'C')
    process.getUnit('oil heater second stage').setOutPressure(ProcessInput.secondStagePressure,'bara')
    process.getUnit('oil heater third stage').setOutTemperature(ProcessInput.thirdStageTemperature,'C')
    process.getUnit('oil heater third stage').setOutPressure(ProcessInput.thirdStagePressure,'bara')
    process.getUnit('export oil cooler').setOutTemperature(ProcessInput.export_oil_temperature,'C')
    process.getUnit('export oil cooler').setOutPressure(ProcessInput.export_oil_pressure,'bara')
    process.getUnit('1st stage cooler').setOutTemperature(ProcessInput.suctionCoolerTemperature,'C')
    process.getUnit('1st stage compressor').setOutletPressure(ProcessInput.firstStageRecompressorPressure)
    process.getUnit('1st stage cooler2')
    process.getUnit('1st stage cooler2').setOutTemperature(ProcessInput.suctionCoolerTemperature,'C')
    process.getUnit('2nd stage compressor').setOutletPressure(ProcessInput.secondStagePressure)
    process.getUnit('2nd stage cooler').setOutTemperature(ProcessInput.suctionCoolerTemperature,'C')
    process.getUnit('3rd stage compressor').setOutletPressure(ProcessInput.firstStagePressure)
    process.getUnit('dew point cooler').setOutTemperature(ProcessInput.dew_point_scrubber_temperature,'C')
    process.getUnit('export gas compressor').setOutletPressure(ProcessInput.export_gas_pressure, 'bara')
    process.getUnit('export gas cooler').setOutTemperature(ProcessInput.export_gas_temperature,'C')



def getoutput():
    # update output
    outputparam = {
        'mass_balance': oilprocess.getUnit('HP well stream').getFlowRate('kg/hr')+oilprocess.getUnit('LP well stream').getFlowRate('kg/hr')-oilprocess.getUnit('export gas').getFlowRate('kg/hr')-oilprocess.getUnit('export oil').getFlowRate('kg/hr'),
        'recompressor1_power': oilprocess.getUnit('1st stage compressor').getPower()/1e3,
        'recompressor2_power': oilprocess.getUnit('2nd stage compressor').getPower()/1e3,
        'recompressor3_power': oilprocess.getUnit('3rd stage compressor').getPower()/1e3,
        'exportcompressor_power': oilprocess.getUnit('export gas compressor').getPower()/1e3,
        'oilexportflow':oilprocess.getUnit('export oil').getFlowRate('m3/hr'),
        'gasexportflow':oilprocess.getUnit('export gas').getFlowRate('MSm3/day'),
    }
    return outputparam


if __name__ == "__main__":
    # Test running the oil process

    # Read input
    inputparam = {
        'feedGasFlowRateHP': 11.65,
        'feedGasFlowRateLP': 5.65,
        'firstStagePressure': 60.0,
        'firstStageTemperature': 70.0,
        'secondStagePressure': 30.0,
        'secondStageTemperature': 80.0,
        'thirdStagePressure': 1.8,
        'thirdStageTemperature': 64.0,
        'export_oil_temperature': 55.0,
        'export_oil_pressure': 8.8,
        'firstStageRecompressorPressure': 6.5,
        'dew_point_scrubber_temperature': 30.0,
        'export_gas_pressure': 130.0,
        'export_gas_temperature': 55.0,
        'suctionCoolerTemperature': 30.0
    }

    # Create oil process
    oilprocess = getprocess()

    # update input in model
    updateinput(process=oilprocess, locinput=ProcessInput(**inputparam))

    # run calculation for aximum 60 sec
    thread = oilprocess.runAsThread()
    thread.join(60*1000)

    if thread.isAlive():
        thread.stop()
        raise Exception(
            f"Oilgas process calculation did not converge within 5 minutes"
        )

    # read and print results
    results = ProcessOutput(**getoutput())
    print(results.__dict__)
