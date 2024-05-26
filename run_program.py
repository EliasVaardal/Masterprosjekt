"""
This module acts as the main simulation of the program, utilizing all classes
in the program-module. It contains the class RunProgram, which


testing code, utilizing all classes in the uncertainty calculation program.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table

# Presents data.
from collect_data import CollectData
from hrs_config import HRSConfiguration
from uncertainty_tools import UncertaintyTools
from correction import Correction
from simulate_hrs import GenerateFlowData
from flow_calculations import FlowProperties

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
        self.flowproperties = FlowProperties()

        self.flowrates_g_s = None
        self.flowrates_kg_min = None
        self.uncertainties = None

    def run_simulation(self, k):
        """
        1. Generates kg/sec flowrates.
        2. Times by 60 to get kg/min flowrates, sampled per second.
        """
        print(vars(self.hrs_config))
        # Flowrate of kg/sec values. Max 0.06kg/s
        flowrates_kg_sec, pressures, temperatures = self.simulator.generate_filling_protocol_kg_sec(5)

        # Flowrate of kg/min values, printed each second. Max 3.6
        flowrate_kgmin_per_second = [x * 60 for x in flowrates_kg_sec]

        timer = 0
        index = 0
        total_mass_delivered = 0
        abs_cfm_uncertainties_std = []
        uncertainties_95 = []
        rel_temp_cont = []
        rel_pres_cont = []
        rel_annual_cont = []
        abs_temp_cont = []
        abs_pres_cont = []
        abs_an_cont = []
        abs_total_unc_std = []
        print("Simulating mass flow for a HRS with a 95% confidence interval")

        for flowrate in flowrate_kgmin_per_second:  # For løkke med kg/min verdier.
            total_mass_delivered += flowrate / 60
            temperature = temperatures[index]
            pressure = pressures[index]
            index += 1
            # Get the abs std cfm uncertainty per flow rate
            uncertainty_std_cfm = self.uncertainty_tools.calculate_cfm_abs_unc_std(
                flowrate
            )

            # Get the absolute cfm + temp + press + annual standard uncertainty
            uncertainty_std_total = self.uncertainty_tools.calculate_total_abs_unc_std(
                flowrate, temperature, pressure)

            # Get the cfm + temp pres annual relative uncertainy 
            rel_uncertainty_95 = self.uncertainty_tools.calculate_cfm_rel_unc_95(
                flowrate, temperature, pressure, k
            )
            # Save to lists
            abs_cfm_uncertainties_std.append(uncertainty_std_cfm)
            abs_total_unc_std.append(uncertainty_std_total)
            uncertainties_95.append(rel_uncertainty_95)

            print(
            f"Time: {timer} seconds - Flow rate: {np.around(flowrate, 2)} kg/min ± {np.around(rel_uncertainty_95,3)}%"
            )

            timer += 1
            # Calculate the different contributions per flowrate, and append them to their respective lists.
            rel_tt, rel_pp, rel_aa, abs_tt, abs_pp, abs_aa = self.uncertainty_tools.return_misc_press_data(flowrate, pressure, temperature, k)
            rel_temp_cont.append(rel_tt)
            rel_pres_cont.append(rel_pp)
            rel_annual_cont.append(rel_aa)
            abs_temp_cont.append(abs_tt)
            abs_pres_cont.append(abs_pp)
            abs_an_cont.append(abs_aa)
            self.hrs_config.previous_temperature = temperature

        # Convert temp and pres to K and Pa for correction format.
        self.correction.post_fill_pressure = pressure * 100000
        self.correction.post_fill_temp = temperature + 273.15

        # Calculate the total error, vented error and dead volume error in kg.
        total_error, vented_mass, dead_mass = self.correction.calculate_total_correction_error(
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
        )

        # Calculate and return the ABSOLUTE vent and dead volume uncertainty.
        abs_vent_unc, abs_dv_unc = self.uncertainty_tools.return_abs_error_data(
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp)
        
        # Calculates the mass error, and total confidence uncertanity
        self.present_mass_data(
            total_mass_delivered,
            abs_total_unc_std,
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
            k
        )
        #Korregert masse
        mass_corrected = total_mass_delivered - total_error

        #Basert på liste med abs usikkerheter -> returnerer total
        tta, ppa, ana, cfma = self.uncertainty_tools.return_total_system_abs_uncs(abs_cfm_uncertainties_std, abs_temp_cont, abs_pres_cont, abs_an_cont, k)
        
        #Kalkulerer relativ usikkerheter.
        rel_tt, rel_pp, rel_an, rel_vv, rel_dv, rel_cfm = self.uncertainty_tools.return_total_system_rel_uncs(mass_corrected, abs_cfm_uncertainties_std, abs_dv_unc,abs_vent_unc, abs_temp_cont, abs_pres_cont, abs_an_cont, k)
        
        plt.rcParams['font.family'] = 'Times New Roman'
        #self.plot_simulation_variables(flowrate_kgmin_per_second, pressures, temperatures)
        #self.plot_relative_simulation(flowrates_kg_sec, uncertainties_95)
        #self.plot_uncertainty_contributions(uncertainties_95, rel_temp_cont, rel_pres_cont, rel_annual_cont,flowrate_kgmin_per_second)
        #self.present_mass_correction_table(dead_mass, vented_mass, dv_unc, vv_unc, total_mass_delivered)
        #self.create_bar_chart(tta, ppa, ana, abs_vent_unc, abs_dv_unc, cfma)
        #self.create_pie_charts(rel_tt, rel_pp, rel_an, rel_vv, rel_dv, rel_cfm, 0.09)
        self.run_mass_errors()

    def run_mass_errors(self):
        volume_vent = 0.00025
        volume_dv = 0.0025
        pressures_1 = [700, 700,700]
        pressures_2 = [180, 350, 550]
        bar_to_Pa = 100000
        dv_mass = []
        vv_mass = []
        rel_dv_unc = []
        rel_vv_unc = []
        temperature = 233.15 #-40 Degrees celsius
        for pressures1,pressure2 in zip(pressures_1,pressures_2):
            previous_density = self.flowproperties.calculate_hydrogen_density(pressures1*bar_to_Pa, temperature)
            current_density = self.flowproperties.calculate_hydrogen_density(pressure2*bar_to_Pa, temperature)
            dv = self.correction.calculate_dead_volume_mass_error(previous_density, current_density, volume_dv)
            vv = self.correction.calculate_vented_mass_error(volume_vent, current_density)
            dv_mass.append(dv)
            vv_mass.append(vv)

            abs_dv_unc = self.uncertainty_tools.caclulate_dead_volume_abs_unc(pressures1*bar_to_Pa, temperature, pressure2*bar_to_Pa, temperature, volume_dv)
            abs_vv_unc = self.uncertainty_tools.calculate_depress_abs_unc(pressure2*bar_to_Pa, temperature)
            print(abs_dv_unc)
            if dv == 0:
                rel_dv_unc.append(0)
            else:
                rel_dv_uncc = abs(abs_dv_unc/dv)*100
                rel_dv_unc.append(rel_dv_uncc)
            rel_vv_unc.append((abs_vv_unc/vv)*100)

        df = pd.DataFrame({
            "Previous Pressure [bar]": pressures_1,
            "Current Pressure [bar]": pressures_2,
            "Dead Volume [kg] (± rel. unc., k=1)": [f"{vol:.4f} ± {unc:.1%}" for vol, unc in zip(dv_mass, rel_dv_unc)],
            "Vented Volume [kg] (± rel. unc., k=1)": [f"{vol:.4f} ± {unc:.1%}" for vol, unc in zip(vv_mass, rel_vv_unc)]
        })

        # Create a figure and a single subplot
        fig, ax = plt.subplots(figsize=(11, 4))  # Adjusted dimensions

        # Hide axes
        ax.axis('off')  # Ensures that all axes are turned off

        # Create the table
        the_table = plt.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')

      # Adjust row heights
        default_row_height = 0.1  # Adjust this value based on your needs
        for key, cell in the_table.get_celld().items():
            row, col = key
            if row > 0:  # Only adjust the rows with data, not the header
                cell.set_height(default_row_height)

        # Adjust font size
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(12)  # Set a larger font size if needed
        # Adjust layout and scale table
        fig.tight_layout()
        the_table.scale(1, 1.4)  # Adjust the scale factor for vertical size as needed
        # Show the plot
        plt.show()



    def create_bar_chart(self, abs_tt, abs_pp, abs_an, abs_vv, abs_dv, abs_cfm, log_scale=True):
        # Labels for the contributions
        labels = ['CFM uncertainty', 'Temperature effect', 'Pressure effect', 'Long-term drift', 'Vented mass', 'Dead volume mass']
        print(f"Deadddvolumeee abs unc: {abs_dv}  Venteeeed abs unc: {abs_vv}")
        # Values for each absolute contribution
        values = np.array([abs_cfm, abs_tt, abs_pp, abs_an, abs_vv, abs_dv])
        
        fig, ax = plt.subplots(figsize=(10,6))
        
        # Optionally use a logarithmic scale
        if log_scale:
            ax.set_yscale('log')
            ylabel = 'Log of Absolute Uncertainty'
        else:
            ylabel = 'Absolute Uncertainty'
        
        # Colors for each section
        colors = ['Blue','crimson','yellowgreen','magenta', 'springgreen','darkorange']
        
        # Create bar chart
        bars = plt.bar(labels, values, color=colors)
        plt.xticks(rotation=0, ha='center', fontsize=10)  # Rotate labels to 45 degrees
        # Adding the value labels on top of each bar
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2 , yval, f"{yval:.2e} kg", ha='center', va='bottom')  # Using scientific notation
        plt.ylabel(ylabel)
        plt.title('Absolute uncertainty contributions k=1')
        plt.show()

    def present_mass_correction_table(self, dead_volume_error, vent_volume_error, uncertainty_dead, uncertainty_vent, measured_mass):
        """
        Creates a visual table showing the measured mass, corrections, and uncertainties.
        """
        # Calculate the corrected mass
        corrected_mass = measured_mass - dead_volume_error - vent_volume_error

        # Calculate the combined uncertainty using quadrature
        total_uncertainty = ((uncertainty_dead**2 + uncertainty_vent**2)**0.5) * 1000

        # Data to be presented in the table
        data = [
            ["Measured Mass", "{:.3f}".format(measured_mass), ""],
            ["Dead Volume Error", "{:.3f}".format(dead_volume_error), "±{:.3f}".format(uncertainty_dead*1000)],
            ["Vent Volume Error", "{:.3f}".format(vent_volume_error), "±{:.3f}".format(uncertainty_vent*1000)],
            ["Corrected Mass", "{:.3f}".format(corrected_mass),  "±{:.3f}".format(total_uncertainty)]
            ]

        # Column headers
        column_labels = ["Parameter", "Value [kg]", "Uncertainty [g]"]

        # Create the table
        fig, ax = plt.subplots(figsize=(8, 4))  # Adjust the figure size as needed
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=data, colLabels=column_labels, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)  # Adjust font size as needed
        table.scale(1, 1.4)  # Adjust table scale as needed

        # Setting the cell borders
        for key, cell in table.get_celld().items():
            cell.set_edgecolor('black')

        plt.title("Mass Measurement Correction and Uncertainty Table")
        #plt.savefig(filename, bbox_inches='tight', dpi=300)  # Saves the figure
        plt.show()

    def plot_uncertainty_contributions(self, cfm_unc, temp_cont, pres_cont, an_cont, flowrates):
        plt.figure(figsize=(12, 8))
        
        # Velg en fargepalett som er behagelig og enkel å skille mellom
        colors = ['blue', 'crimson', 'magenta', 'yellowgreen']
        labels = [
            'CFM Uncertainty', 'Temperature Contribution',
            'Pressure Contribution', 'Annual Deviation Contribution'
        ]
        lines = ['-', '-', '-', '-']  # Bruk kontinuerlige linjer for klarhet
        
        # Plot data med valgte attributter
        for data, color, label, line in zip([cfm_unc, temp_cont, pres_cont, an_cont], colors, labels, lines):
            plt.plot(flowrates, data, label=label, linestyle=line, color=color, marker='', linewidth=2)

        plt.yscale('log')  # Bruk logaritmisk skala for y-aksen
        plt.title('Uncertainty Contributions Across Different Flowrates')
        plt.xlabel('Flowrate (m^3/s)')
        plt.ylabel('Relative Uncertainty (log scale)')  # Presiser at skalaen er logaritmisk i y-aksen label
        plt.legend()
        plt.grid(True, which="both", linestyle='--', linewidth=0.5)  # Tilpass gridlinjene for bedre lesbarhet
        plt.show()

    def plot_simulation_variables(self, flowrates_kg_sec, pressures, temperature):
        """
        Plots the simulation flowrate, pressure and temperature based on a
        fueling protocol.

        Parameters:
            - Flowrates in kg/sec
        
        """
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
        Plots the flowrate against its relative uncertainties with reduced clutter,
        including both upper and lower uncertainty bounds.
        """
        # Konverter til numpy arrays
        flowrate_kg_sec = np.array(flowrate_kg_sec)
        uncertainties_kg_sec_relative = np.array(uncertainties_kg_sec_relative)

        # Konverter kg/sec til kg/min
        flowrate_kg_min = flowrate_kg_sec * 60

        # Reduser antall punkter ved å velge hvert n-te punkt
        n = 1  # Juster dette tallet etter behov for å balansere detaljnivå og oversikt
        flowrate_thinned = flowrate_kg_min[::n]
        uncertainties_thinned = uncertainties_kg_sec_relative[::n]

        plt.figure(figsize=(10, 5))

        # Plot de opprinnelige målingene
        plt.scatter(flowrate_thinned, uncertainties_thinned, color='blue', label='Measured Uncertainty', s=10, alpha=0)
        
        # Plot speilet usikkerhet for å vise både øvre og nedre usikkerhet
        plt.scatter(flowrate_thinned, -uncertainties_thinned, color='blue', s=10, alpha=0)

        # Lineær interpolasjon mellom de opprinnelige punktene
        if len(flowrate_thinned) > 1:
            sort_index = np.argsort(flowrate_thinned)
            x_sorted = flowrate_thinned[sort_index]
            y_sorted = uncertainties_thinned[sort_index]
            
            plt.plot(x_sorted, y_sorted, 'k--', label='Upper Bound Interpolation')
            plt.plot(x_sorted, -y_sorted, 'k--', label='Lower Bound Interpolation')

        plt.title("Flowrate vs Relative Uncertainty")
        plt.xlabel("Flowrate (kg/min)")
        plt.ylabel("Relative Uncertainty (%)")
        plt.grid(True)
        plt.axhline(0, color="red", linewidth=0.5)  # Zero line for reference
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
        total_error, mass_error_vv, mass_error_dv = self.correction.calculate_total_correction_error(
            self.correction.pre_fill_pressure,
            self.correction.pre_fill_temp,
            self.correction.post_fill_pressure,
            self.correction.post_fill_temp,
        )
        # Corrects
        mass_corrected = tot_mass_delivered - total_error

        # Calculates total uncertainty: CFM(cfm+p+t+ad))  + DV + Vent
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
        tot_fill_unc_95 = tot_fill_unc_95*3
        data = [["Total mass delivered (after correction)", f"{mass_corrected:.3f} kg ± {tot_fill_unc_95:.1f} %"]]

        # Table creation with size adjustments
        fig, ax = plt.subplots(figsize=(8, 1))  # Adjust figure size as needed
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=data, colLabels=["Description", "Value"], cellLoc = 'center', loc='center')

        # Style adjustments
        table.auto_set_font_size(False)
        table.set_fontsize(12)  # Adjust fontsize according to your preference
        table.scale(1.5, 1.5)  # Adjust scaling factor to change cell size

        plt.subplots_adjust(left=0.2, right=0.8, top=0.6, bottom=0.4)
        
        #plt.show()


    def create_pie_charts(self, rel_tt, rel_pp, rel_an, rel_vv, rel_dv, rel_cfm, zoom_threshold):
        # Labels for each category
        labels = ['Temperature Uncertainty', 'Pressure Uncertainty', 'Analytical Uncertainty', 
                'Vented Volume Uncertainty', 'Dead Volume Uncertainty', 'CFM Uncertainty']

        # Relative uncertainties as values
        values = [rel_tt, rel_pp, rel_an, rel_vv, rel_dv, rel_cfm]
        
        # Calculate the total to determine the threshold for 'small' and 'large' slices.
        total = sum(values)
        small_slices_threshold = total * zoom_threshold

        # Define custom colors
        custom_colors = ["crimson", "magenta", "yellowgreen", "springgreen", "darkorange", "royalblue"]

        fig, ax = plt.subplots(1, 2, figsize=(14, 7))

        # Determine which labels to display in the left pie (only show labels for larger uncertainties)
        large_labels = [label if value >= small_slices_threshold else '' for label, value in zip(labels, values)]

        # Set a balanced pie chart size for both
        pie_chart_radius = 1.0  # Balanced size for both pie charts

        # Left pie chart
        wedges, texts, autotexts = ax[0].pie(
            values, labels=large_labels, autopct=lambda p: f'{p:.1f}%' if (p / 100 * total) >= small_slices_threshold else '',
            startangle=90, colors=custom_colors, radius=pie_chart_radius
        )
        ax[0].set_title('Total Relative Uncertainty')

        # Manually adjust position of "Dead Volume Uncertainty" label, if needed
        for text, label in zip(texts, labels):
            if label == 'Dead Volume Uncertainty':
                text.set_horizontalalignment('right')
                text.set_position((text.get_position()[0]*1.1, text.get_position()[1]))

        # Quarter view pie chart for small slices (similar size)
        small_values = [value for value in values if value < small_slices_threshold]
        small_labels = [label for label, value in zip(labels, values) if value < small_slices_threshold]
        if small_values:
            ax[1].pie(small_values, labels=small_labels, autopct=lambda p: f"{p * sum(small_values) / total:.2f}%", startangle=90, radius=pie_chart_radius, colors=custom_colors)
            ax[1].set_title('Detailed View of Minor Uncertainties')
        else:
            ax[1].text(0.5, 0.5, 'No minor uncertainties to display', horizontalalignment='center', verticalalignment='center')
            ax[1].set_title('Detailed View of Minor Uncertainties')
            ax[1].axis('off')

        plt.tight_layout()
        plt.show()
                
program = RunProgram()
program.run_simulation(1)
