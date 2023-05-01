"""
TEG process module
"""
from neqsim import jNeqSim
from pydantic.dataclasses import dataclass
from pydantic import Field

@dataclass
class TEGprocess():
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
    feedGasFlowRate: float = Field(11.65, ge=0.0, le=100.0, title="Feed gas flow rate (not saturated) [MSm3/day]")
    leanTEGFlowRate: float = Field(5500.0, ge=0.0, le=100000.0, title="Lean TEG Flow Rate [kg/hr]")
    process = jNeqSim.processSimulation.processSystem.ProcessSystem()

    def createprocess(self):
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
        dryFeedGas.setFlowRate(self.feedGasFlowRate, "MSm3/day")
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
        TEGFeed.setFlowRate(self.leanTEGFlowRate, "kg/hr")
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

        self.process = jNeqSim.processSimulation.processSystem.ProcessSystem()
        self.process.add(dryFeedGas)
        self.process.add(saturatedFeedGas)
        self.process.add(waterSaturatedFeedGas)
        self.process.add(TEGFeed)
        self.process.add(absorber)
        self.process.add(dehydratedGas)
        return self.process

@dataclass
class TEGprocessOutput():
    """Output validation model"""
    waterInDryGasppm: float | None = None
    waterInWetGasppm: float | None = None

def updatetinput(process, locinput):
    process.getUnit('dry feed gas').setFlowRate(locinput['feedGasFlowRate'], 'MSm3/day')
    process.getUnit('lean TEG to absorber').setFlowRate(locinput['leanTEGFlowRate'], 'kg/hr')

if __name__ == "__main__":
    #Test of running the class
    input = {
        'feedGasFlowRate': 11.65,
        'leanTEGFlowRate': 5500.0
    }
    tegprocess = TEGprocess(**input)
    tegprocess.createprocess()
    tegprocess.process.run()
    assert tegprocess.feedGasFlowRate == 11.65

    output = {
        'waterInDryGasppm' : tegprocess.process.getUnit('dry gas from absorber').getFluid().getComponent('water').getx()*1e6,
        'waterInWetGasppm' : tegprocess.process.getUnit('water saturated feed gas').getFluid().getComponent('water').getx()*1e6
    }
    results = TEGprocessOutput(**output)
    print(results.__dict__)
    print(results.waterInDryGasppm)


    input = {
        'feedGasFlowRate': 12.65,
        'leanTEGFlowRate': 6500.0
    }

    updatetinput(process=tegprocess.process, locinput=input)
    tegprocess.process.run()

    output = {
        'waterInDryGasppm' : tegprocess.process.getUnit('dry gas from absorber').getFluid().getComponent('water').getx()*1e6,
        'waterInWetGasppm' : tegprocess.process.getUnit('water saturated feed gas').getFluid().getComponent('water').getx()*1e6
    }
    results = TEGprocessOutput(**output)
    print(results.__dict__)
    print(results.waterInDryGasppm)