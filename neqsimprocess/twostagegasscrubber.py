"""
Two stage hydrocarbon dew point process
...
The module is used for simulation of a two stage dew point scrubber process and 
setting input parameters and reading output from a simulation
"""
from functools import cache
from neqsim import jNeqSim
from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass
class ProcessInput():
    """
    A class to define input for a simulation of a two stage scruber hydrocarbon dew point process

    ...

    Attributes
    ----------
    pressure_scrubber1 : float
        the operating pressure of scrubber 1 
    temperature_scrubber1 : float
        the operating temperature of scrubber 1 
    pressure_scrubber2 : float
        the operating pressure of scrubber 2 
    temperature_scrubber2 : float
        the operating temperature of scrubber 2 
    """
    pressure_scrubber1: float = Field(
        50.0, ge=10.0, le=150.0, title="the operating pressure of scrubber 1 (bara)")
    temperature_scrubber1: float = Field(
        25.0, ge=0.0, le=200.0, title="The operating temperature of scrubber 1 [C]")
    pressure_scrubber2: float = Field(
        70.0, ge=10.0, le=150.0, title="the operating pressure of scrubber 2 (bara)")
    temperature_scrubber2: float = Field(
        12.0, ge=0.0, le=200.0, title="The operating temperature of scrubber 2 [C]")
    liquid_entrainment_fraction_scrubber2: float = Field(
        12.0, ge=0.0, le=1.0, title="The fraction of liquid entering scrubber 2 that will follow the gas from the scrubber [-]")


@dataclass
class ProcessOutput():
    """
    A class to define output results from a simulation of a two stage scruber hydrocarbon dew point process

    ...

    Attributes
    ----------
    cricondenbar : float
        the cricondebar of the gas (bara)
    dewpointpressure_0C : float
        the dew point pressure at 0C (bara)
    """
    cricondenbar: float | None = None
    dewpointpressure_0C: float | None = None
    c6_pluss : float | None = None


@cache
def getprocess():
    """
    The method creates a two stage hydrocarbon dew point process
    """
    feedGas = jNeqSim.thermo.system.SystemSrkEos(
        273.15 + 42.0, 10.00)
    feedGas.addComponent("nitrogen", 1.03)
    feedGas.addComponent("CO2", 1.42)
    feedGas.addComponent("methane", 83.88)
    feedGas.addComponent("ethane", 8.07)
    feedGas.addComponent("propane", 3.54)
    feedGas.addComponent("i-butane", 0.54)
    feedGas.addComponent("n-butane", 0.84)
    feedGas.addComponent("i-pentane", 0.21)
    feedGas.addComponent("n-pentane", 0.19)
    feedGas.addComponent("n-hexane", 0.28)
    feedGas.addComponent("n-heptane", 0.28)
    feedGas.setMixingRule(10)
    feedGas.setMultiPhaseCheck(True)

    feedGas = jNeqSim.processSimulation.processEquipment.stream.Stream(
        "feed gas", feedGas)
    feedGas.setFlowRate(1.0, "MSm3/day")
    feedGas.setTemperature(25.0, "C")
    feedGas.setPressure(50.0, "bara")

    feedseparator = jNeqSim.processSimulation.processEquipment.separator.Separator(
        "separator 1", feedGas)
    
    cooler1 = jNeqSim.processSimulation.processEquipment.heatExchanger.Heater("cooler", feedseparator.getGasOutStream())
    cooler1.setOutPressure(70.0, 'bara')
    cooler1.setOutTemperature(12.0, 'C')

    dewpointscrubber = jNeqSim.processSimulation.processEquipment.separator.ThreePhaseSeparator(
        "dew point scrubber", cooler1.getOutStream())
    dewpointscrubber.setEntrainment(0.5, "volume", "feed", "oil","gas")


    process = jNeqSim.processSimulation.processSystem.ProcessSystem()
    process.add(feedGas)
    process.add(feedseparator)
    process.add(cooler1)
    process.add(dewpointscrubber)
    return process


def updateinput(process, locinput):
    """
    update process with input parameters
    """
    process.getUnit('feed gas').setTemperature(
        locinput.temperature_scrubber1, 'C')
    process.getUnit('feed gas').setPressure(
        locinput.pressure_scrubber1, 'bara')

    process.getUnit('cooler').setOutTemperature(
        locinput.temperature_scrubber2, 'C')
    process.getUnit('cooler').setOutPressure(
        locinput.pressure_scrubber2, 'bara')
    
    process.getUnit('dew point scrubber').setEntrainment(locinput.liquid_entrainment_fraction_scrubber2, "volume", "feed", "oil","gas")


def getoutput():
    # update output

    #Calculate cricondebar
    ccb = hcprocess.getUnit('dew point scrubber').getGasOutStream().CCB("bara")

    #Calculate dew point pressure
    fluid = hcprocess.getUnit('dew point scrubber').getGasOutStream().getFluid()
    fluid.setTemperature(0.0, "C")
    fluid.setPressure(20.0, "bara")
    cvd_sim = jNeqSim.PVTsimulation.simulation.SaturationPressure(fluid)
    cvd_sim.run()
    dewppres = float(cvd_sim.getSaturationPressure())

    #C6 pluss estimation
    c6_pluss = fluid.getComponent('n-hexane').getz() + fluid.getComponent('n-heptane').getz()

    outputparam = {
        'cricondenbar': ccb,
        'dewpointpressure_0C': dewppres,
        'c6_pluss': c6_pluss
    }
    return outputparam


if __name__ == "__main__":
    # Test running the HC dew point process

    # Read input
    inputparam = {
        'temperature_scrubber1': 25.0,
        'pressure_scrubber1': 50.0, 
        'temperature_scrubber2': 12.0,
        'pressure_scrubber2': 70.0, 
        'liquid_entrainment_fraction_scrubber2': 0.5
    }

    # Create dew point process
    hcprocess = getprocess()

    # update input in model
    updateinput(process=hcprocess, locinput=ProcessInput(**inputparam))

    # run calculation
    thread = hcprocess.runAsThread()
    thread.join(1*60*1000)

    if thread.isAlive():
        thread.stop()
        raise Exception(
            f"The model did not converge within 1 minute"
        )

    # read and print results
    results = ProcessOutput(**getoutput())
    print(results.__dict__)
