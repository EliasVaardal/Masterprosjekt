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

# self.file_path = r"C:\Path\To\Your\Master_project_sheet.xlsx"
# self.file_path = "C:/Path/To/Your/Master_project_sheet.xlsx"
# self.file_path = r"C:\Users\elias\OneDrive\Dokumenter\unc_calc_sheet.xlsx"


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
        self.file_path = r"C:\Users\Elias\Downloads\unc_calc_sheet_2.xlsx"
        self.hrs_config = HRSConfiguration()
        self.data_reader = CollectData(self.hrs_config, self.file_path)
        self.data_reader.read_file()
        self.data_reader.gather_data_config()
        self.correction = Correction(self.hrs_config)
        self.uncertainty_tools = UncertaintyTools(self.hrs_config, self.correction)

        self.simulator = GenerateFlowData()

        self.flowrates_g_s = None
        self.flowrates_kg_min = None
        self.uncertainties = None

    def run_simulation_kg_sec(self):
        """
        1. Generates kg/sec flowrates.
        2. Times by 60 to get kg/min flowrates, sampled per second.
        """
        flowrates_kg_sec = self.simulator.generate_flowrate_kg_sec(6)
        flowrate_kgmin_per_second = [x * 60 for x in flowrates_kg_sec]
        timer = 0
        total_mass_delivered = 0
        uncertainties_95 = []
        uncertainties_std = []

        print("Simulating mass flow for a HRS with a 95% confidence interval")

        for flowrate in flowrate_kgmin_per_second:  # For løkke med kg/min verdier.
            total_mass_delivered += flowrate / 60
            flowrate_reference = flowrate / 60  # TODO: Sjekk!
            rel_uncertainty_95 = (
                self.uncertainty_tools.calculate_relative_uncertainty_95(
                    flowrate, flowrate_reference
                )
            )  # TODO: BLIR DITTA RETT?
            uncertainty_std = (
                self.uncertainty_tools.calculate_absolute_std_uncertainty_cfm(flowrate)
            )

            print(
                f"Time: {timer} seconds - Flow rate: {np.around(flowrate, 2)} kg/min ± {np.around(rel_uncertainty_95, 2)}%"
            )
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

    def plotpqqw(self, data_kg_sec, uncertainties_kg_sec_relative, time_intervals):
        absolute_uncertainties_kg_min = (relative_uncertainties_percent / 100) * flow_rates_kg_min

        # Plott flow rates med usikkerhetsstolper
        plt.errorbar(
            time_seconds,
            flow_rates_kg_min,
            yerr=absolute_uncertainties_kg_min,
            fmt='o',
            label='Flow rate with relative uncertainty',
            capsize=5,
            ecolor='red'
        )

        # For å fremheve den relative usikkerheten, kan du også plotte den direkte
        plt.twinx()  # Opprett en annen y-akse for den relative usikkerheten
        plt.plot(
            time_seconds,
            relative_uncertainties_percent,
            label='Relative uncertainty (%)',
            color='green'
        )

        plt.xlabel('Time (seconds)')
        plt.ylabel('Flow rate (kg/min)')
        plt.title('Flow Rate Simulation with Relative Uncertainty')
        plt.grid(True)
        plt.legend()
        plt.show()


    def present_mass_data(
        self,
        total_mass_delivered,
        uncertainties_std,
        prev_filling_pressure,
        prev_filling_temperature,
        final_filling_pressure,
        final_filling_temperature,
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
        mass_corrected = total_mass_delivered - total_error
        total_uncertainty_filling_95 = self.uncertainty_tools.calculate_total_system_relative_uncertainty_confidence(
            mass_corrected,
            uncertainties_std,
            prev_filling_pressure,
            prev_filling_temperature,
            final_filling_pressure,
            final_filling_temperature,
            k,
        )
        print("Total mass delivered (before correction):", total_mass_delivered, "kg")
        print(
            f"Total mass delivered (after correction): {mass_corrected} ± {total_uncertainty_filling_95} %"
        )
        self.correction.check_correction(prev_filling_pressure, final_filling_pressure)

    ####################################################################################################

    def run_simulation_g_s(self):
        """
        Utilizes the simulation program to generate flowdata. The uncertainty
        of each flowrate is then calculated, based on data from the Excel template,
        at the end of the filling correction applied, and data will be plotted.

        Parameters:
            - None

        Returns:
            - None
        """
        self.flowrates_g_s = self.simulator.generate_flowrate_grams_seconds(6)
        print("Simulating mass flow for a HRS with a 95% confidence interval")
        total_mass_delivered = 0
        uncertainties_95 = []
        uncertainties_std = []

        for flowrate in self.flowrates_g_s:
            # print(flowrate, type(flowrate))
            total_mass_delivered += flowrate
            # uncertainty = self.uncertainty_tools.calculate_relative_uncertainty_95(
            #    flowrate * 3.6
            # )
            uncertainty_std = (
                self.uncertainty_tools.calculate_absolute_std_uncertainty_cfm(
                    flowrate * 3.6
                )
            )

            # uncertainties_95.append(uncertainty)
            uncertainties_std.append(uncertainty_std)
            print(
                #    f"Flow rate: {np.around(flowrate,2)} ± {np.around(uncertainty,2)}%  [g/s]  Total mass delivered: {total_mass_delivered}"
            )
        self.present_mass_data(
            total_mass_delivered
            / 1000,  # Turn into kg, to follow code usual unit direction
            uncertainties_std,
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
            2,
        )
        self.plot_simulation(
            self.flowrates_g_s, uncertainties_std, np.arange(len(self.flowrates_g_s))
        )

    def plot_simulation(self, data, uncertainties, time_intervals):
        # Husk å gi credz.

        # Konverter usikkerhetene til et numpy-array for enkel håndtering
        uncertainties = np.array(uncertainties)

        # Plott data med feilfelt som har større tykkelse og tupper (caps)
        plt.errorbar(
            time_intervals,
            data,
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
            data - uncertainties,
            data + uncertainties,
            color="gray",
            alpha=0.2,
        )

        plt.xlabel("Time (seconds)")
        plt.ylabel("Total Mass Delivered (kg)")
        plt.title("Hydrogen Tank Filling Simulation")
        plt.grid(True)
        plt.legend()
        plt.show()


program = RunProgram()
program.run_simulation_kg_sec()
# program.run_simulation_kgmin()
