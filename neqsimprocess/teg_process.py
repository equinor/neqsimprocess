"""
TEG process module
"""
from functools import cache
from neqsim import jNeqSim
from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass
class ProcessInput():
    """
    A class to represent a TEG dehydration process.

    ...

    Attributes
    ----------
    feedGasFlowRate : float
        the flow rate of the feed gas to the dehdyration process in unit MSm3/day
    flowrateTEG : float
        the flow rate of lean TEG to the dehdyration process in unit kg/hr

    Methods
    -------
    getProcess():
        get the process simulation object
    """
    feedGasFlowRate: float = Field(
        11.65, ge=0.0, le=100.0, title="Feed gas flow rate (not saturated) [MSm3/day]")
    leanTEGFlowRate: float = Field(
        5500.0, ge=0.0, le=100000.0, title="Lean TEG Flow Rate [kg/hr]",)


@dataclass
class ProcessOutput():
    """Output validation model"""
    waterInDryGasppm: float | None = None
    waterInWetGasppm: float | None = None

@cache
def getprocess():
    """
    create TEG process simulation object
    """
    feedGas = jNeqSim.thermo.system.SystemSrkCPAstatoil(
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
    feedGas.addComponent("water", 0.0)
    feedGas.addComponent("TEG", 0)
    feedGas.setMixingRule(10)
    feedGas.setMultiPhaseCheck(True)

    dryFeedGas = jNeqSim.processSimulation.processEquipment.stream.Stream(
        "dry feed gas", feedGas)
    dryFeedGas.setFlowRate(ProcessInput.feedGasFlowRate.default, "MSm3/day")
    dryFeedGas.setTemperature(30.4, "C")
    dryFeedGas.setPressure(52.21, "bara")

    saturatedFeedGas = jNeqSim.processSimulation.processEquipment.util.StreamSaturatorUtil(
        dryFeedGas)
    saturatedFeedGas.setName("water saturator")

    waterSaturatedFeedGas = jNeqSim.processSimulation.processEquipment.stream.Stream(
        saturatedFeedGas.getOutStream())
    waterSaturatedFeedGas.setName("water saturated feed gas")

    feedTEG = feedGas.clone()
    feedTEG.setMolarComposition(
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.03, 0.97])

    TEGFeed = jNeqSim.processSimulation.processEquipment.stream.Stream(
        "lean TEG to absorber", feedTEG)
    TEGFeed.setFlowRate(ProcessInput.leanTEGFlowRate.default, "kg/hr")
    TEGFeed.setTemperature(43.0, "C")
    TEGFeed.setPressure(52.21, "bara")

    absorber = jNeqSim.processSimulation.processEquipment.absorber.SimpleTEGAbsorber()
    absorber.setName("TEG absorber")
    absorber.addGasInStream(waterSaturatedFeedGas)
    absorber.addSolventInStream(TEGFeed)
    absorber.setNumberOfStages(5)
    absorber.setStageEfficiency(0.55)

    dehydratedGas = jNeqSim.processSimulation.processEquipment.stream.Stream(
        absorber.getGasOutStream())
    dehydratedGas.setName("dry gas from absorber")

    richTEG = jNeqSim.processSimulation.processEquipment.stream.Stream(
        absorber.getSolventOutStream())
    richTEG.setName("rich TEG from absorber")

    process = jNeqSim.processSimulation.processSystem.ProcessSystem()
    process.add(dryFeedGas)
    process.add(saturatedFeedGas)
    process.add(waterSaturatedFeedGas)
    process.add(TEGFeed)
    process.add(absorber)
    process.add(dehydratedGas)
    process.add(richTEG)
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
    # Test of running the class

    # Read input
    inputparam = {
        'feedGasFlowRate': 11.65,
        'leanTEGFlowRate': 5500.0
    }

    # Create TEG process
    tegprocess = getprocess()

    #update input in model
    updateinput(process=tegprocess, locinput=ProcessInput(**inputparam))

    # run calculation
    thread = tegprocess.runAsThread()
    thread.join(5*60*1000)

    if thread.isAlive():
        thread.stop()
        raise Exception(
            f"The Martin Linge TEG dehydartion calculation did not converge within 5 minutes"
        )
    
    #read results
    results = ProcessOutput(**getoutput())

    print(results.__dict__)
    print(results.waterInDryGasppm)
