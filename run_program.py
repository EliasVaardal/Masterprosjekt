"""
This module acts as the main simulation of the program, utilizing all classes
in the program-module. It contains the class RunProgram, which


testing code, utilizing all classes in the uncertainty calculation program.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

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
        flowrates_kg_sec, pressures, temperatures = (
            self.simulator.generate_flowrate_kg_sec(6)
        )

        # Flowrate of kg/min values, printed each second. Max 3.6
        flowrate_kgmin_per_second = [x * 60 for x in flowrates_kg_sec]

        timer = 0
        index = 0
        total_mass_delivered = 0
        abs_uncertainties_std = []
        uncertainties_95 = []
        temp_cont = []
        pres_cont = []
        annual_cont = []
        dv_unc = None
        vv_unc = None

        print("Simulating mass flow for a HRS with a 95% confidence interval")

        for flowrate in flowrate_kgmin_per_second:  # For løkke med kg/min verdier.
            temperature = temperatures[index]
            pressure = pressures[index]
            index += 1

            total_mass_delivered += flowrate / 60
            uncertainty_std = self.uncertainty_tools.calculate_cfm_abs_unc_std(
                flowrate, temperature, pressure
            )

            rel_uncertainty_95 = self.uncertainty_tools.calculate_cfm_rel_unc_95(
                flowrate, temperature, pressure, 1
            )
            abs_uncertainties_std.append(uncertainty_std)
            uncertainties_95.append(rel_uncertainty_95)
            #print(
            #f"Time: {timer} seconds - Flow rate: {np.around(flowrate, 2)} kg/min ± {np.around(rel_uncertainty_95,3)}%"
            #)
            timer += 1
            tt, pp, aa = self.uncertainty_tools.return_misc_press_data(flowrate, pressure, temperature)
            temp_cont.append(tt)
            pres_cont.append(pp)
            annual_cont.append(aa)

        # Convert temp and pres to K and Pa
        self.correction.post_fill_pressure = pressure * 100000
        self.correction.post_fill_temp = temperature + 273.15

        vv_unc, dv_unc = self.uncertainty_tools.return_error_data(
            total_mass_delivered,
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
            1)

        self.present_mass_data(
            total_mass_delivered,
            abs_uncertainties_std,
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
            2,
        )
        self.plot_variables(flowrate_kgmin_per_second, pressures, temperatures)
        self.plot_relative_simulation(flowrates_kg_sec, uncertainties_95)
    
    def plot_uncertainty_contributions(self, cfm_unc, temp_cont, pres_cont, an_cont, vv_unc, dv_unc, flowrates):



    def plot_variables(self, flowrates_kg_sec, pressures, temperature):
        # Create a figure and a set of subplots gpt
        fig, ax1 = plt.subplots()

        # Plotting the flowrates with x-axis as the index of data points
        color = "tab:red"
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Flowrates (kg/sec)", color=color)
        ax1.plot(flowrates_kg_sec, color=color)
        ax1.tick_params(axis="y", labelcolor=color)

        # Creating a second y-axis for pressures using the same x-axis
        ax2 = ax1.twinx()
        color = "tab:blue"
        ax2.set_ylabel("Pressures", color=color)
        ax2.plot(pressures, color=color)
        ax2.tick_params(axis="y", labelcolor=color)

        # Creating a third axis object by cloning the first axis
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("axes", 1.2))  # Offset the right spine
        color = "tab:green"
        ax3.set_ylabel("Temperature", color=color)
        ax3.plot(temperature, color=color)
        ax3.tick_params(axis="y", labelcolor=color)

        # Adding a title and a legend
        plt.title("Flowrates, Pressures, and Temperature vs. Time")
        fig.tight_layout()  # Adjusts the plot to make room for the right y-label
        # Show the plot
        plt.show()

    def plot_relative_simulation(self, flowrate_kg_sec, uncertainties_kg_sec_relative):
        """
        Plots the flowrate against its relative uncertainties. gpt
        #TODO: bedre docstrings. 
        Args:
        flowrate_kg_sec (array): List or array containing flowrate values in kg/sec.
        uncertainties_kg_sec_relative (array): List or array containing relative 
        uncertainties corresponding to the flowrates.
        time_intervals (array): Time intervals; not used in plotting in this example, 
        included as per function signature.
        """
        flowrate_kg_min = [rate * 60 for rate in flowrate_kg_sec]

        # Array conversion for mathematical operations
        x = np.array(flowrate_kg_min)
        y = np.array(uncertainties_kg_sec_relative)

        # Using Spline for smooth curve
        spline_positive = UnivariateSpline(x, y, s=1)  # Smoothing factor
        spline_negative = UnivariateSpline(x, -y, s=1)  # Mirrored spline

        # Generating more points to create a smooth line
        x_dense = np.linspace(min(x), max(x), 300)
        y_dense_positive = spline_positive(x_dense)
        y_dense_negative = spline_negative(x_dense)

        # Plot
        plt.figure(figsize=(10, 5))
        plt.plot(x_dense, y_dense_positive, label="Upper Uncertainty", color="black")
        plt.plot(x_dense, y_dense_negative, label="Lower Uncertainty", color="black")
        plt.title("Flowrate vs Relative Uncertainty")
        plt.xlabel("Flowrate (kg/min)")
        plt.ylabel("Relative Uncertainty (%)")
        plt.grid(True)
        plt.axhline(0, color="red", linewidth=0.5)  # Zero line for reference
        plt.ylim(
            min(y_dense_negative) * 1.1, max(y_dense_positive) * 1.1
        )  # Ensure the plot includes both extremities
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
        This method utilizes different methods to calculate and presents filling data.

        Parameters:
            - Total mass delivered: The uncorrected mass delivered [kg]
            - Uncertainties_std: Array with absolute standard CFM filling uncertainties [kg/min]
            - Pre-filling-pressure: The pressure of the previous refueling [Pa]
            - Pre-filling-temperature: The temperature of the previous refueling [Kelvin]
            - Post-filling-pressure: The pressure of the current refueling [Pa]
            - Post-filling-temperature: The temperature of the current refueling [Kelvin]

        Returns:
            - None
        """

        # Calculates total error
        total_error = self.correction.calculate_total_correction_error(
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
        )
        # Corrects
        mass_corrected = tot_mass_delivered - total_error

        # Calculates total uncertainty: CFM + DV + Vent
        tot_fill_unc_95 = self.uncertainty_tools.calculate_total_system_rel_unc_95(
            mass_corrected,
            uncertainties_std,
            pre_fill_press,
            pre_fill_temp,
            post_fill_press,
            post_fill_temp,
            k,
        )
        # Prints results.
        print("Total mass delivered (before correction):", tot_mass_delivered, "kg")
        print(
            f"Total mass delivered (after correction): {mass_corrected}kg ± {tot_fill_unc_95} %"
        )
        self.correction.check_correction(pre_fill_press, post_fill_press)


program = RunProgram()
program.run_simulation()
