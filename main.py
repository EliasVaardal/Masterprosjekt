"""
main()
This module contains the main testing code, utilizing all classes in the uncertainty calculation program.
"""

import numpy as np
import matplotlib.pyplot as plt

from collect_data import CollectData
from hrs_config import HRSConfiguration
from simulate_hrs import GenerateFlowData
from correction import Correction
from uncertainty_tools import UncertaintyTools

class simulate_and_calculate_flow:
    """
    This class utilizes all avaliable classes to generate massflow data(Class GenerateFlowData),
    read data input from the Excel file (CollectData), store data as a HRS configuration(HRSConfig),
    calculate uncertainty based on file data(UncertaintyTools), correct the errors (Correction)
    and finally contains methods to present the data.
    """
    def __init__(self) -> None:
        self.data_reader = CollectData()
        self.data_reader.read_file()

        self.hrs_config = HRSConfiguration(self.data_reader)


        self.simulation = GenerateFlowData()
        self.uncertainty = UncertaintyTools()
        self.correction = Correction()

        self.total_mass_delivered = 0
        self.uncertanties = []

    def time_simulation_seconds(self):
        """
        The goal of the code is to simulate one filling of a FCEV tank, which is usually around 5-6kg. 
        """ 

        self.uncertainty.gather_data()
        massflow_simulation = self.simulation.generate_simulation_mean_seconds()

        print("Simulating mass flow for a HRS with a 95% confidence interval")
        time_intervals = np.arange(len(massflow_simulation))  # Assuming each massflow represents a 10-second interval
        
        for massflow in massflow_simulation:
            self.total_mass_delivered += massflow
            uncertainty = self.uncertainty.calculate_relative_uncertainty(massflow*600) # 600, as we are doing 10sec time increments. I THInk #TODO sjekk conversion rate.
            self.uncertanties.append(uncertainty)
            print(f"Flow rate: {np.around(massflow,2)} ± {np.around(uncertainty,2)}%  kg/min ")

        # Regner ut korregeringer.
        dead_volume = self.correction.calculate_dead_volume()
        self.correction.check_correction(self.total_mass_delivered, dead_volume)


        self.plot_simulation(massflow_simulation, self.uncertanties, time_intervals )

    def plot_simulation(self, data, uncertainties, time_intervals):
        print(len(data), len(self.uncertanties))
        plt.errorbar(time_intervals, data, yerr=np.array(uncertainties)/100 , fmt='o', label='Data with uncertainty')
        plt.xlabel('Time (10 seconds)')
        plt.ylabel('Total Mass Delivered (kg)')
        plt.title('Hydrogen Tank Filling Simulation')
        plt.grid(True)
        plt.legend()
        plt.show()



data_presenter = PresentData()
data_presenter.time_simulation_seconds()