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
        self.simulator.generate_flowrate_grams_seconds()

        self.flowrates_g_s = None
        self.uncertainties = None

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
        uncertainties = []

        for flowrate in self.flowrates_g_s:
            #print(flowrate, type(flowrate))
            total_mass_delivered += flowrate
            uncertainty = self.uncertainty_tools.calculate_relative_uncertainty_95(
                (flowrate)*(3.6) # Times 3.6 to do correct interpolation as flowrate values are kg/hr.
            )  # Her er flowraten i g/s.
            uncertainties.append(uncertainty)
            print(
                f"Flow rate: {np.around(flowrate,2)} ± {np.around(uncertainty,2)}%  [g/s]  Total mass delivered: {total_mass_delivered}"
            )
        self.present_mass_data(total_mass_delivered, uncertainties, self.correction.pressure_subsequent, self.correction.temperature_subsequent, 2)
        self.plot_simulation(self.flowrates_g_s, uncertainties, np.arange(len(self.flowrates_g_s)))

    def present_mass_data(self, total_mass_delivered, uncertainties, final_filling_pressure, final_filling_temperature, k):
        total_error = self.correction.calculate_total_correction_error(self.correction.pressure_initial, self.correction.temperature_initial, self.correction.pressure_subsequent, self.correction.temperature_subsequent)
        total_uncertainty_filling_95 = self.uncertainty_tools.calculate_total_relative_system_uncertainty_confidence(total_mass_delivered, uncertainties, final_filling_pressure, final_filling_temperature, k)
        print("Total mass delivered (before correction):", total_mass_delivered, "grams")
        print(f"Total mass delivered (after correction): {total_mass_delivered-total_error} ± {total_uncertainty_filling_95} %")


   
    def run_simulation_kgmin(self):
        """
        Work in progress, needs testing.
        """
        flowrates_kg_min = self.simulator.generate_flowrate_kg_min()
        print("Simulating mass flow for a HRS with a 95% confidence interval")
        total_mass_delivered = 0
        uncertainties = []

        for flowrate in flowrates_kg_min:
            print(flowrate)
            total_mass_delivered += flowrate
            uncertainty = self.uncertainty_tools.calculate_relative_uncertainty_95(
                flowrate
            )  # Her er flowraten i g/s.
            uncertainties.append(uncertainty)
            print(
                f"Flow rate: {np.around(flowrate,2)} ± {np.around(uncertainty,2)}%  kg/min"
            )

    def plot_simulation(self, data, uncertainties, time_intervals):
        # Husk å gi credz.

        # Konverter usikkerhetene til et numpy-array for enkel håndtering
        uncertainties = np.array(uncertainties)

        # Plott data med feilfelt som har større tykkelse og tupper (caps)
        plt.errorbar(time_intervals, data, yerr=uncertainties, fmt='o', label='Data with uncertainty',
                    elinewidth=2, capsize=5, capthick=2, ecolor='red')

        # Alternativt kan du bruke fylte områder for å representere usikkerheten
        plt.fill_between(time_intervals, data - uncertainties, data + uncertainties, color='gray', alpha=0.2)

        plt.xlabel('Time (seconds)')
        plt.ylabel('Total Mass Delivered (kg)')
        plt.title('Hydrogen Tank Filling Simulation')
        plt.grid(True)
        plt.legend()
        plt.show()

program = RunProgram()
program.run_simulation_g_s()
#program.run_simulation_kgmin()
