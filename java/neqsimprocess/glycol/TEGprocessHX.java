package neqsim.processSimulation.util.example;

import java.io.ObjectInputStream.GetField;

import neqsim.processSimulation.processEquipment.absorber.SimpleTEGAbsorber;
import neqsim.processSimulation.processEquipment.absorber.WaterStripperColumn;
import neqsim.processSimulation.processEquipment.distillation.Condenser;
import neqsim.processSimulation.processEquipment.distillation.DistillationColumn;
import neqsim.processSimulation.processEquipment.distillation.Reboiler;
import neqsim.processSimulation.processEquipment.heatExchanger.Cooler;
import neqsim.processSimulation.processEquipment.heatExchanger.HeatExchanger;
import neqsim.processSimulation.processEquipment.heatExchanger.Heater;
import neqsim.processSimulation.processEquipment.mixer.StaticMixer;
import neqsim.processSimulation.processEquipment.pump.Pump;
import neqsim.processSimulation.processEquipment.stream.EnergyStream;
import neqsim.processSimulation.processEquipment.stream.Stream;
import neqsim.processSimulation.processEquipment.util.Calculator;
import neqsim.processSimulation.processEquipment.util.Recycle;
import neqsim.processSimulation.processEquipment.util.StreamSaturatorUtil;
import neqsim.processSimulation.processEquipment.valve.ThrottlingValve;
import neqsim.processSimulation.processSystem.ProcessSystem;
import neqsim.thermodynamicOperations.flashOps.SaturateWithWater;
import neqsim.processSimulation.processEquipment.separator.Separator;

public class TEGdehydrationProcessDistillation {

	public static void main(String[] args) {

		// Create the input fluid to the TEG process and saturate it with water at
		// scrubber conditions
		neqsim.thermo.system.SystemInterface feedGas = new neqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 42.0,
				10.00);
		feedGas.addComponent("nitrogen", 1.03);
		feedGas.addComponent("CO2", 1.42);
		feedGas.addComponent("methane", 83.88);
		feedGas.addComponent("ethane", 8.07);
		feedGas.addComponent("propane", 3.54);
		feedGas.addComponent("i-butane", 0.54);
		feedGas.addComponent("n-butane", 0.84);
		feedGas.addComponent("i-pentane", 0.21);
		feedGas.addComponent("n-pentane", 0.19);
		feedGas.addComponent("n-hexane", 0.28);
		feedGas.addComponent("water", 0.0);
		feedGas.addComponent("TEG", 0);
		feedGas.createDatabase(true);
		feedGas.setMixingRule(10);
		feedGas.setMultiPhaseCheck(true);

		Stream dryFeedGas = new Stream("dry feed gas", feedGas);
		dryFeedGas.setFlowRate(11.23, "MSm3/day");
		dryFeedGas.setTemperature(30.4, "C");
		dryFeedGas.setPressure(52.21, "bara");

		StreamSaturatorUtil saturatedFeedGas = new StreamSaturatorUtil(dryFeedGas);
		saturatedFeedGas.setName("water saturator");

		Stream waterSaturatedFeedGas = new Stream(saturatedFeedGas.getOutStream());
		waterSaturatedFeedGas.setName("water saturated feed gas");

		neqsim.thermo.system.SystemInterface feedTEG = (neqsim.thermo.system.SystemInterface) feedGas.clone();
		feedTEG.setMolarComposition(new double[] { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.03, 0.97 });

		Stream TEGFeed = new Stream("lean TEG to absorber", feedTEG);
		TEGFeed.setFlowRate(6862.5, "kg/hr");
		TEGFeed.setTemperature(43.0, "C");
		TEGFeed.setPressure(52.21, "bara");

		SimpleTEGAbsorber absorber = new SimpleTEGAbsorber();
		absorber.setName("TEG absorber");
		absorber.addGasInStream(waterSaturatedFeedGas);
		absorber.addSolventInStream(TEGFeed);
		absorber.setNumberOfStages(5);
		absorber.setStageEfficiency(0.55);

		Stream dehydratedGas = new Stream(absorber.getGasOutStream());
		dehydratedGas.setName("dry gas from absorber");
		Stream richTEG = new Stream(absorber.getSolventOutStream());
		richTEG.setName("rich TEG from absorber");

		ThrottlingValve glycol_flash_valve = new ThrottlingValve("Flash valve", richTEG);
		glycol_flash_valve.setName("Rich TEG HP flash valve");
		glycol_flash_valve.setOutletPressure(4.9);

		Heater richGLycolHeaterCondenser = new Heater(glycol_flash_valve.getOutStream());
		richGLycolHeaterCondenser.setName("rich TEG preheater");


		HeatExchanger heatEx2 = new HeatExchanger(richGLycolHeaterCondenser.getOutStream());
		heatEx2.setName("rich TEG heat exchanger 1");
		heatEx2.setGuessOutTemperature(273.15+62.0);
		heatEx2.setUAvalue(220.0);
		

		Separator flashSep = new Separator(heatEx2.getOutStream(0));
		flashSep.setName("degasing separator");

		Stream flashGas = new Stream(flashSep.getGasOutStream());
		flashGas.setName("gas from degasing separator");

		Stream flashLiquid = new Stream(flashSep.getLiquidOutStream());
		flashLiquid.setName("liquid from degasing separator");

		HeatExchanger heatEx = new HeatExchanger(flashLiquid);
		heatEx.setName("rich TEG heat exchanger 2");
		heatEx.setGuessOutTemperature(273.15+130.0);
		heatEx.setUAvalue(600.0);

		ThrottlingValve glycol_flash_valve2 = new ThrottlingValve("LP flash valve", heatEx.getOutStream(0));
		glycol_flash_valve2.setName("Rich TEG LP flash valve");
		glycol_flash_valve2.setOutletPressure(1.23);

		neqsim.thermo.system.SystemInterface stripGas = (neqsim.thermo.system.SystemInterface) feedGas.clone();
		stripGas.setMolarComposition(new double[] { 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 });

		Stream strippingGas = new Stream("stripGas", stripGas);
		strippingGas.setFlowRate(90.0, "Sm3/hr");
		strippingGas.setTemperature(80.0, "C");
		strippingGas.setPressure(1.23, "bara");

		Stream gasToReboiler = (Stream) strippingGas.clone();
		gasToReboiler.setName("gas to reboiler");

		DistillationColumn column = new DistillationColumn(2, true, true);
		column.setName("TEG regeneration column");
		column.addFeedStream(glycol_flash_valve2.getOutStream(), 2);
		column.getReboiler().setOutTemperature(273.15 + 206.6);
		column.getCondenser().setOutTemperature(273.15 + 100.0);
		column.getReboiler().addStream(gasToReboiler);
		column.setTopPressure(1.2);
		column.setBottomPressure(1.23);

		Heater coolerRegenGas = new Heater(column.getGasOutStream());
		coolerRegenGas.setName("regen gas cooler");
		coolerRegenGas.setOutTemperature(273.15 + 35.5);

		Separator sepregenGas = new Separator(coolerRegenGas.getOutStream());
		sepregenGas.setName("regen gas separator");

		Stream gasToFlare = new Stream(sepregenGas.getGasOutStream());
		gasToFlare.setName("gas to flare");

		Stream liquidToTrreatment = new Stream(sepregenGas.getLiquidOutStream());
		liquidToTrreatment.setName("water to treatment");

		WaterStripperColumn stripper = new WaterStripperColumn("TEG stripper");
		stripper.addSolventInStream(column.getLiquidOutStream());
		stripper.addGasInStream(strippingGas);
		stripper.setNumberOfStages(4);
		stripper.setStageEfficiency(0.5);

		Recycle recycleGasFromStripper = new Recycle("stripping gas recirc");
		recycleGasFromStripper.addStream(stripper.getGasOutStream());
		recycleGasFromStripper.setOutletStream(gasToReboiler);
		
		Heater bufferTank = new Heater("TEG buffer tank", stripper.getSolventOutStream());
		bufferTank.setOutTemperature(273.15+185.0);
		
		Pump hotLeanTEGPump = new Pump(bufferTank.getOutStream());// stripper.getSolventOutStream());
		hotLeanTEGPump.setName("hot lean TEG pump");
		hotLeanTEGPump.setOutletPressure(20.0);
		hotLeanTEGPump.setIsentropicEfficiency(0.75);

		heatEx.setFeedStream(1, hotLeanTEGPump.getOutStream());

		heatEx2.setFeedStream(1, heatEx.getOutStream(1));
	
		Heater coolerhOTteg3 = new Heater(heatEx2.getOutStream(1));
		coolerhOTteg3.setName("lean TEG cooler");
		coolerhOTteg3.setOutTemperature(273.15 + 43.0);

		Pump hotLeanTEGPump2 = new Pump(coolerhOTteg3.getOutStream());
		hotLeanTEGPump2.setName("lean TEG HP pump");
		hotLeanTEGPump2.setOutletPressure(52.21);
		hotLeanTEGPump2.setIsentropicEfficiency(0.75);

		Stream leanTEGtoabs = new Stream(hotLeanTEGPump2.getOutStream());
		leanTEGtoabs.setName("lean TEG to absorber");

		neqsim.thermo.system.SystemInterface pureTEG = (neqsim.thermo.system.SystemInterface) feedGas.clone();
		pureTEG.setMolarComposition(new double[] { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0 });

		Stream makeupTEG = new Stream("makeup TEG", pureTEG);
		makeupTEG.setFlowRate(1e-6, "kg/hr");
		makeupTEG.setTemperature(43.0, "C");
		makeupTEG.setPressure(52.21, "bara");

		Calculator makeupCalculator = new Calculator("makeup calculator");
		makeupCalculator.addInputVariable(dehydratedGas);
		makeupCalculator.addInputVariable(flashGas);
		makeupCalculator.addInputVariable(gasToFlare);
		makeupCalculator.addInputVariable(liquidToTrreatment);
		makeupCalculator.setOutputVariable(makeupTEG);

		StaticMixer makeupMixer = new StaticMixer("makeup mixer");
		makeupMixer.addStream(leanTEGtoabs);
		makeupMixer.addStream(makeupTEG);

		Recycle resycleLeanTEG = new Recycle("lean TEG resycle");
		resycleLeanTEG.addStream(makeupMixer.getOutStream());
		resycleLeanTEG.setOutletStream(TEGFeed);
		resycleLeanTEG.setPriority(200);
		resycleLeanTEG.setDownstreamProperty("flow rate");

		richGLycolHeaterCondenser.setEnergyStream(column.getCondenser().getEnergyStream());
		//richGLycolHeater.isSetEnergyStream();

		neqsim.processSimulation.processSystem.ProcessSystem operations = new neqsim.processSimulation.processSystem.ProcessSystem();
		operations.add(dryFeedGas);
		operations.add(saturatedFeedGas);
		operations.add(waterSaturatedFeedGas);
		operations.add(TEGFeed);
		operations.add(absorber);
		operations.add(dehydratedGas);
		operations.add(richTEG);
		operations.add(glycol_flash_valve);
		operations.add(richGLycolHeaterCondenser);
		operations.add(heatEx2);
		operations.add(flashSep);
		operations.add(flashGas);
		operations.add(flashLiquid);
		operations.add(heatEx);
		operations.add(glycol_flash_valve2);
		operations.add(gasToReboiler);
		operations.add(column);
		operations.add(coolerRegenGas);
		operations.add(sepregenGas);
		operations.add(gasToFlare);
		operations.add(liquidToTrreatment);
		operations.add(strippingGas);
		operations.add(stripper);
		operations.add(recycleGasFromStripper);
		operations.add(bufferTank);
		operations.add(hotLeanTEGPump);
		operations.add(coolerhOTteg3);
		operations.add(hotLeanTEGPump2);
		operations.add(leanTEGtoabs);
		operations.add(makeupCalculator);
		operations.add(makeupTEG);
		operations.add(makeupMixer);
		operations.add(resycleLeanTEG);

		operations.run();
		// operations.run();

		operations.save("c:/temp/TEGprocessHX.neqsim");
		/// operations = ProcessSystem.open("c:/temp/TEGprocess.neqsim");
		// ((DistillationColumn)operations.getUnit("TEG regeneration
		/// column")).setTopPressure(1.2);
		// operations.run();
		// ((DistillationColumn)operations.getUnit("TEG regeneration
		/// column")).setNumberOfTrays(2);
		System.out.println("water in wet gas  " + ((Stream) operations.getUnit("water saturated feed gas")).getFluid()
				.getPhase(0).getComponent("water").getz() * 1.0e6 * 0.01802 * 101325.0 / (8.314 * 288.15));
		System.out.println("water in dry gas  " + ((Stream) operations.getUnit("dry gas from absorber")).getFluid()
				.getPhase(0).getComponent("water").getz() * 1.0e6);
		System.out.println("reboiler duty (KW) "
				+ ((Reboiler) ((DistillationColumn) operations.getUnit("TEG regeneration column")).getReboiler())
						.getDuty() / 1.0e3);
		System.out.println("wt lean TEG " + ((WaterStripperColumn) operations.getUnit("TEG stripper"))
				.getSolventOutStream().getFluid().getPhase("aqueous").getWtFrac("TEG") * 100.0);

		double waterInWetGasppm = waterSaturatedFeedGas.getFluid().getPhase(0).getComponent("water").getz() * 1.0e6;
		double waterInWetGaskgMSm3 = waterInWetGasppm * 0.01802 * 101325.0 / (8.314 * 288.15);
		double TEGfeedwt = TEGFeed.getFluid().getPhase("aqueous").getWtFrac("TEG");
		double TEGfeedflw = TEGFeed.getFlowRate("kg/hr");
		double waterInDehydratedGasppm = dehydratedGas.getFluid().getPhase(0).getComponent("water").getz() * 1.0e6;
		double waterInDryGaskgMSm3 = waterInDehydratedGasppm * 0.01802 * 101325.0 / (8.314 * 288.15);
		double richTEG2 = richTEG.getFluid().getPhase("aqueous").getWtFrac("TEG");
		System.out.println("reboiler duty (KW) " + ((Reboiler) column.getReboiler()).getDuty() / 1.0e3);
		System.out.println("flow rate from reboiler "
				+ ((Reboiler) column.getReboiler()).getLiquidOutStream().getFlowRate("kg/hr"));
		System.out.println("flow rate from stripping column " + stripper.getLiquidOutStream().getFlowRate("kg/hr"));
		System.out.println("flow rate from pump2  " + hotLeanTEGPump2.getOutStream().getFluid().getFlowRate("kg/hr"));
		System.out.println("makeup TEG  " + makeupTEG.getFluid().getFlowRate("kg/hr"));

		TEGFeed.getFluid().display();
		absorber.run();

		System.out.println("pump power " + hotLeanTEGPump.getDuty());
		System.out.println("pump2 power " + hotLeanTEGPump2.getDuty());
		System.out.println("wt lean TEG after reboiler "
				+ column.getLiquidOutStream().getFluid().getPhase("aqueous").getWtFrac("TEG"));
		System.out.println("temperature from pump " + (hotLeanTEGPump2.getOutStream().getTemperature() - 273.15));

		System.out.println("flow rate from reboiler "
				+ ((Reboiler) column.getReboiler()).getLiquidOutStream().getFlowRate("kg/hr"));
		System.out.println("flow rate from pump2  " + hotLeanTEGPump2.getOutStream().getFluid().getFlowRate("kg/hr"));
		System.out.println("condenser duty  "
				+ ((Condenser) ((DistillationColumn) operations.getUnit("TEG regeneration column")).getCondenser())
						.getDuty() / 1.0e3);
		System.out.println(
				"richGLycolHeaterCondenser duty  " + richGLycolHeaterCondenser.getEnergyStream().getDuty() / 1.0e3);
		System.out.println("richGLycolHeaterCondenser temperature out  "
				+ richGLycolHeaterCondenser.getOutStream().getTemperature("C"));
		richGLycolHeaterCondenser.run();

		hotLeanTEGPump.getOutStream().displayResult();
		flashLiquid.displayResult();

		System.out.println("Temperature rich TEG out of reflux condenser " + richGLycolHeaterCondenser.getOutStream().getTemperature("C"));
		heatEx.displayResult();
		System.out.println("glycol out temperature " + glycol_flash_valve2.getOutStream().getFluid().getTemperature("C"));
		System.out.println("glycol out temperature2 " +heatEx2.getOutStream(0).getTemperature("C"));
		System.out.println("glycol out temperature2 " +heatEx2.getOutStream(1).getTemperature("C"));
	
	
		System.out.println("out water rate LP valve" + glycol_flash_valve2.getOutStream().getFluid().getPhase(0).getComponent("water").getNumberOfmoles());
		System.out.println("glycol out water rate reboil " + ((Reboiler) column.getReboiler()).getLiquidOutStream().getFluid().getComponent("water").getNumberOfmoles());
		System.out.println("glycol out water rate condens " + ((Condenser) column.getCondenser()).getGasOutStream().getFluid().getComponent("water").getNumberOfmoles());
		System.out.println("recycle out water rate  " +recycleGasFromStripper.getOutletStream().getFluid().getComponent("water").getNumberOfmoles());
	}
}
