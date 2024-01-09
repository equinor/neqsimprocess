"""
TEG process module
...
The module is sed for establishing a TEG process, 
setting input parameters and reading output from a simulation
"""
from functools import cache
from neqsim import jNeqSim
from pydantic.dataclasses import dataclass
from pydantic import Field


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
    feedGasFlowRate: float = Field(
        11.65, ge=0.0, le=100.0, title="Feed gas flow rate (not saturated) [MSm3/day]")
    leanTEGFlowRate: float = Field(
        5500.0, ge=0.0, le=100000.0, title="Lean TEG Flow Rate [kg/hr]",)


@dataclass
class ProcessOutput():
    """
    A class to define output results from a TEG dehydration process simulation.

    ...

    Attributes
    ----------
    waterInDryGasppm : float
        the water content of the dehdyrated gas in ppm (vol)
    waterInWetGasppm : float
        the water content of the saturated feed gas in ppm (vol)
    """
    waterInDryGasppm: float | None = None
    waterInWetGasppm: float | None = None


@cache
def getprocess():
    """
    The method creates a TEG process simulation object using neqsim
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
        "dry feed gas", feedGas)
    feedGas.setFlowRate(ProcessInput.feedGasFlowRate, "MSm3/day")
    feedGas.setTemperature(25.0, "C")
    feedGas.setPressure(55.0, "bara")

    feedseparator = jNeqSim.processSimulation.processEquipment.separator.Separator(
        "feed gas", feedGas)
    
    cooler1 = jNeqSim.processSimulation.processEquipment.heatExchanger(feedseparator.getGasOutStream())
    cooler1.setOutPressure(75.0, 'bara')
    cooler1.setOutTemperature(13.0, 'C')

    dewpointscrubber = jNeqSim.processSimulation.processEquipment.separator.ThreePhaseSeparator(
        "dew point scrubber", cooler1.getOutStream())
    dewpointscrubber.setEntrainment(0.5, "volume", "feed", "oil","gas")

    #calculate dew point pressure of gas from scrubber
    
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
    process.getUnit('dry feed gas').setFlowRate(
        locinput.feedGasFlowRate, 'MSm3/day')
    process.getUnit('lean TEG to absorber').setFlowRate(
        locinput.leanTEGFlowRate, 'kg/hr')


def getoutput():
    # update output
    outputparam = {
        'waterInDryGasppm': tegprocess.getUnit('dry gas from absorber').getFluid().getComponent('water').getx()*1e6,
        'waterInWetGasppm': tegprocess.getUnit('water saturated feed gas').getFluid().getComponent('water').getx()*1e6
    }
    return outputparam


if __name__ == "__main__":
    # Test running the TEG process

    # Read input
    inputparam = {
        'feedGasFlowRate': 11.65,
        'leanTEGFlowRate': 5500.0
    }

    # Create TEG process
    tegprocess = getprocess()

    # update input in model
    updateinput(process=tegprocess, locinput=ProcessInput(**inputparam))

    # run calculation
    thread = tegprocess.runAsThread()
    thread.join(5*60*1000)

    if thread.isAlive():
        thread.stop()
        raise Exception(
            f"The Martin Linge TEG dehydartion calculation did not converge within 5 minutes"
        )

    # read and print results
    results = ProcessOutput(**getoutput())
    print(results.__dict__)
