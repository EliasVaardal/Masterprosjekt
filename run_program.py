"""
This module acts as the main simulation of the program, utilizing all classes
in the program-module. It contains the class RunProgram, which


testing code, utilizing all classes in the uncertainty calculation program.
"""

import numpy as np
import matplotlib.pyplot as plt

# Presents data.
from collect_data import CollectData
from hrs_config import HRSConfiguration
from uncertainty_tools import UncertaintyTools
from correction import Correction
from simulate_hrs import GenerateFlowData

class RunProgram:
    """
    This class utilizes all avaliable classes to generate massflow data(Class GenerateFlowData),
    read data input from the Excel file (CollectData), store data as a HRS configuration(HRSConfig),
    calculate uncertainty based on file data(UncertaintyTools), correct the errors (Correction)
    and finally contains methods to present the data.
    """

    def __init__(self):
        """
        As the RunProgram object is created, it sets in motion multiple classes, some which
        are used for parameters for others. Furthermore it reads data, and stores it in varaibles.
        """
        self.hrs_config = HRSConfiguration()
        self.data_reader = CollectData(self.hrs_config)
        self.correction = Correction(self.hrs_config)
        self.uncertainty_tools = UncertaintyTools(self.hrs_config, self.correction)
        self.simulator = GenerateFlowData()

        self.flowrates_g_s = None
        self.flowrates_kg_min = None
        self.uncertainties = None

    def run_simulation(self):
        """
        1. Generates kg/sec flowrates.
        2. Times by 60 to get kg/min flowrates, sampled per second.
        """
        print(vars(self.hrs_config))
        # Flowrate of kg/sec values. Max 0.06kg/s
        flowrates_kg_sec = self.simulator.generate_flowrate_kg_sec(6)
        # Flowrate of kg/min values, printed each second. Max 3.6
        flowrate_kgmin_per_second = [x * 60 for x in flowrates_kg_sec]

        timer = 0
        total_mass_delivered = 0
        uncertainties_std = []
        uncertainties_95 = []
        print("Simulating mass flow for a HRS with a 95% confidence interval")

        for flowrate in flowrate_kgmin_per_second:  # For løkke med kg/min verdier.
            total_mass_delivered += flowrate / 60
            rel_uncertainty_95 = self.uncertainty_tools.calculate_cfm_rel_unc_95(flowrate)
            uncertainty_std = self.uncertainty_tools.calculate_cfm_abs_unc_std(flowrate)
            print(f"Time: {timer} seconds - Flow rate: {np.around(flowrate, 2)} kg/min ± {np.around(rel_uncertainty_95, 3)}%")
            uncertainties_95.append(rel_uncertainty_95)
            uncertainties_std.append(uncertainty_std)
            timer += 1

        self.present_mass_data(
            total_mass_delivered,
            uncertainties_std,
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
            2,
        )

        time_intervals = np.arange(len(flowrates_kg_sec))
        self.plot_simulation_kgmin_s(
            flowrates_kg_sec, uncertainties_std, time_intervals
        )

    def plot_simulation_kgmin_s(
        self, data_kg_sec, uncertainties_kg_sec_relative, time_intervals
    ):
        data_kg_min = np.array(data_kg_sec) * 60
        uncertainties = np.array(uncertainties_kg_sec_relative)

        # Plott data med feilfelt som har større tykkelse og tupper (caps)
        plt.errorbar(
            time_intervals,
            data_kg_min,
            yerr=uncertainties,
            fmt="o",
            label="Data with uncertainty",
            elinewidth=2,
            capsize=6,
            capthick=2,
            ecolor="red",
        )

        # Alternativt kan du bruke fylte områder for å representere usikkerheten
        plt.fill_between(
            time_intervals,
            data_kg_min - uncertainties,
            data_kg_min + uncertainties,
            color="gray",
            alpha=0.2,
        )

        plt.xlabel("Time (seconds)")
        plt.ylabel("Flow rate (kg/min)")
        plt.title("Hydrogen Tank Filling Simulation")
        plt.grid(True)
        plt.legend()
        plt.show()

    def present_mass_data(
        self,
        tot_mass_delivered,
        uncertainties_std,
        pre_fill_press,
        pre_fill_temp,
        post_fill_press,
        post_fill_temp,
        k,
    ):
        """
        This method presents filling data.
        """
        total_error = self.correction.calculate_total_correction_error(
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
        )
        mass_corrected = tot_mass_delivered - total_error

        tot_fill_unc_95 = (
            self.uncertainty_tools.calculate_total_system_rel_unc_95(
                mass_corrected,
                uncertainties_std,
                pre_fill_press,
                pre_fill_temp,
                post_fill_press,
                post_fill_temp,
                k,
            )
        )
        print("Total mass delivered (before correction):", tot_mass_delivered, "kg")
        print(
            f"Total mass delivered (after correction): {mass_corrected} ± {tot_fill_unc_95} %"
        )
        self.correction.check_correction(pre_fill_press, post_fill_press)


program = RunProgram()
program.run_simulation()