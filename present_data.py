"""
This module acts as the main simulation of the program, utilizing all classes
in the program-module. It contains the class RunProgram, which


testing code, utilizing all classes in the uncertainty calculation program.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Presents data.
from collect_data import CollectData
from hrs_config import HRSConfiguration
from uncertainty_tools import UncertaintyTools
from correction import Correction
from simulate_hrs import GenerateFlowData
from flow_calculations import FlowProperties


class PresentData:
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

        self.flowrates_kg_sec = None
        self.flowrate_kgmin_per_second = None
        self.pressures = None
        self.temperatures = None

        self.abs_cfm_uncertainties_std = []
        self.rel_cfm_uncs = []
        self.comb_rel_unc_k = []
        self.rel_temp_conts = []
        self.rel_pres_conts = []
        self.rel_ltd_conts = []
        self.abs_temp_conts = []
        self.abs_pres_conts = []
        self.abs_ltd_conts = []
        self.abs_total_uncs_std = []

        self.total_error = None
        self.vented_error = None
        self.dead_volume_error = None
        self.vent_abs_unc = None
        self.dv_abs_unc = None
        self.mass_uncorrected = 0
        self.mass_corrected = 0

        self.tot_rel_temp = None
        self.tot_rel_pres = None
        self.tot_rel_ltd = None
        self.tot_rel_vent = None
        self.tot_rel_dv = None
        self.tot_rel_cfm = None
        self.tot_abs_cfm = None
        self.tot_abs_temp = None
        self.tot_abs_press = None
        self.tot_abs_ltd = None
        self.k = None
        self.total_relative_fill_unc_k = None # THe total filling uncertainty

    def run_simulation(self, k):
        """
        1. Generates kg/sec flowrates.
        2. Times by 60 to get kg/min flowrates, sampled per second.
        """
        self.k = k
        # print(vars(self.hrs_config))
        # Flowrate of kg/sec values. Max 0.06kg/s
        self.flowrates_kg_sec, self.pressures, self.temperatures = (
            self.simulator.generate_filling_protocol_kg_sec(5)
        )

        # Flowrate of kg/min values, printed each second. Max 3.6
        self.flowrate_kgmin_per_second = [x * 60 for x in self.flowrates_kg_sec]

        timer = 0
        index = 0
        print("Simulating mass flow for a HRS with a 95% confidence interval")

        for flowrate in self.flowrate_kgmin_per_second:  # For løkke med kg/min verdier.
            self.mass_uncorrected += flowrate / 60
            temperature = self.temperatures[index]
            pressure = self.pressures[index]
            index += 1
            # Get the abs std cfm uncertainty per flow rate
            uncertainty_std_cfm = self.uncertainty_tools.calculate_cfm_abs_unc_std(
                flowrate
            )

            # Get the absolute cfm + temp + press + annual standard uncertainty
            uncertainty_std_total = self.uncertainty_tools.calculate_total_abs_unc_std(
                flowrate, temperature, pressure
            )

            # Get the cfm + temp pres annual relative uncertainy
            comb_rel_uncertainty_k = self.uncertainty_tools.calculate_cfm_rel_unc_k(
                flowrate, temperature, pressure, self.k
            )

            # Get the cfm rel uncertainty
            cfm_rel_uncertainty = self.uncertainty_tools.calculate_cfm_rel_unc_k(
                flowrate, temperature, pressure, self.k, string="CFM"
            )

            # Save to lists
            self.abs_cfm_uncertainties_std.append(uncertainty_std_cfm)
            self.abs_total_uncs_std.append(uncertainty_std_total)
            self.comb_rel_unc_k.append(comb_rel_uncertainty_k)
            self.rel_cfm_uncs.append(cfm_rel_uncertainty)

            print(
                f"Time: {timer} seconds - Flow rate: {np.around(flowrate, 2)} kg/min ± {np.around(comb_rel_uncertainty_k,3)}%"
            )

            timer += 1
            # Calculate contributions per flowrate, and append to respective lists.
            rel_tt, rel_pp, rel_aa, abs_tt, abs_pp, abs_aa = (
                self.uncertainty_tools.return_misc_press_data(
                    flowrate, pressure, temperature
                )
            )
            self.rel_temp_conts.append(rel_tt)
            self.rel_pres_conts.append(rel_pp)
            self.rel_ltd_conts.append(rel_aa)
            self.abs_temp_conts.append(abs_tt)
            self.abs_pres_conts.append(abs_pp)
            self.abs_ltd_conts.append(abs_aa)
            self.hrs_config.previous_temperature = temperature

        # Convert temp and pres to K and Pa for correction format.
        self.correction.post_fill_pressure = pressure * 100000
        self.correction.post_fill_temp = temperature + 273.15

        # Calculate the total error, vented error and dead volume error in kg.
        self.total_error, self.vented_error, self.dead_volume_error = (
            self.correction.calculate_total_correction_error(
                self.correction.pre_fill_pressure,
                self.correction.pre_fill_temp,
                self.correction.post_fill_pressure,
                self.correction.post_fill_temp,
            )
        )
        self.mass_corrected = self.mass_uncorrected - self.total_error

        # Calculate and return the ABSOLUTE vent and dead volume uncertainty.
        self.vent_abs_unc, self.dv_abs_unc = (
            self.uncertainty_tools.return_abs_error_data(
                self.correction.pre_fill_pressure,
                self.correction.pre_fill_temp,
                self.correction.post_fill_pressure,
                self.correction.post_fill_temp,
            )
        )
        #print(f"Pre T:{self.correction.pre_fill_temp},PreP:{self.correction.pre_fill_pressure}")
        #print(f"Post T:{self.correction.post_fill_temp},PostP:{self.correction.post_fill_pressure}")
        self.present_mass_data(k)

        # Based on the lists, calculate total absolute and relative uncertainties.
        (
            self.tot_rel_temp,
            self.tot_rel_pres,
            self.tot_rel_ltd,
            self.tot_rel_vent,
            self.tot_rel_dv,
            self.tot_rel_cfm,
            self.tot_abs_cfm,
            self.tot_abs_temp,
            self.tot_abs_press,
            self.tot_abs_ltd,
        ) = self.uncertainty_tools.return_total_system_uncs(
            self.mass_corrected,
            self.abs_cfm_uncertainties_std,
            self.dv_abs_unc,
            self.vent_abs_unc,
            self.abs_temp_conts,
            self.abs_pres_conts,
            self.abs_ltd_conts,
        )

        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams.update({"font.size": 14})
        self.plot_simulation_variables()
        self.plot_combined_rel_simulation()
        self.plot_uncertainty_contributions()
        self.present_mass_correction_table()
        self.create_bar_chart()
        self.create_pie_charts(0.09)
        self.run_mass_errors()

    def run_mass_errors(self):
        """
        Presents mass errors based on pressures defined within the function. The method calculates the systematic
        mass errors and its related uncertainties.
        """
        volume_vent = 0.00025
        volume_dv = 0.0025
        pressures_1 = [700, 700, 180, 350, 550]
        pressures_2 = [700, 350, 700, 700, 700]
        bar_to_Pa = 100000
        dv_mass = []
        vv_mass = []
        rel_dv_unc = []
        rel_vv_unc = []
        errors = []
        temperature = 233.15  # -40 Degrees celsius
        for pressures1, pressure2 in zip(pressures_1, pressures_2):
            previous_density = self.flowproperties.calculate_hydrogen_density(
                pressures1 * bar_to_Pa, temperature
            )
            current_density = self.flowproperties.calculate_hydrogen_density(
                pressure2 * bar_to_Pa, temperature
            )
            dv = self.correction.calculate_dead_volume_mass_error(
                previous_density, current_density, volume_dv
            )
            vv = self.correction.calculate_vented_mass_error(
                volume_vent, current_density
            )
            dv_mass.append(dv)
            vv_mass.append(vv)
            error = dv + vv
            errors.append(abs(error) / 1)
            print(f"dv: {dv} v  v: {vv}")

            abs_dv_unc = self.uncertainty_tools.caclulate_dead_volume_abs_unc(
                pressures1 * bar_to_Pa,
                temperature,
                pressure2 * bar_to_Pa,
                temperature,
                volume_dv,
            )
            abs_vv_unc = self.uncertainty_tools.calculate_depress_abs_unc(
                pressure2 * bar_to_Pa, temperature
            )
            if dv == 0:
                rel_dv_unc.append(0)
            else:
                rel_dv_uncc = abs(abs_dv_unc / dv) * 100
                rel_dv_unc.append(rel_dv_uncc)
            rel_vv_unc.append((abs_vv_unc / vv) * 100)
        df = pd.DataFrame(
            {
                "Previous Pressure [bar]": pressures_1,
                "Current Pressure [bar]": pressures_2,
                "Dead Volume [kg] (± rel. unc., k=1)": [
                    f"{vol:.3f} ± {unc:.1%}" for vol, unc in zip(dv_mass, rel_dv_unc)
                ],
                "Vented Volume [kg] (± rel. unc., k=1)": [
                    f"{vol:.3f} ± {unc:.1%}" for vol, unc in zip(vv_mass, rel_vv_unc)
                ],
            }
        )
        # Create a figure and a single subplot
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.axis("off")
        the_table = plt.table(
            cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center"
        )
        default_row_height = 0.1
        for key, cell in the_table.get_celld().items():
            row, col = key
            if row > 0:
                cell.set_height(default_row_height)
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(14)
        fig.tight_layout()
        the_table.scale(1, 1.4)
        plt.show()

    def create_bar_chart(self):
        """
        Presents the total absolute uncertainties, after they have accumlated over the filling process.
        The uncertainties are collected from class parameters.

        Parameters:
            - Log_scale: Boolean value if present as log y axis or not.

        Returns:
            - None
        """
        labels = [
            "CFM uncertainty",
            "Temperature effect",
            "Pressure effect",
            "Long-term drift",
            "Vented mass",
            "Dead volume mass",
        ]
        values = np.array(
            [
                self.tot_abs_cfm,
                self.tot_abs_temp,
                self.tot_abs_press,
                self.tot_abs_ltd,
                self.vent_abs_unc,
                self.dv_abs_unc,
            ]
        )
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_yscale("log")
        ylabel = "Log of Absolute Uncertainty [kg]"
        colors = [
            "Blue",
            "crimson",
            "yellowgreen",
            "magenta",
            "springgreen",
            "darkorange",
        ]
        ax.grid(True, which="both", linestyle="-", linewidth=0.5, axis="y", zorder=0)
        bars = plt.bar(
            labels, values, color=colors, edgecolor="black", linewidth=1.5, zorder=3
        )
        # Create bar chart
        bars = plt.bar(labels, values, color=colors)
        plt.xticks(rotation=0, ha="center", fontsize=10)  # Rotate labels to 45 degrees
        # Adding the value labels on top of each bar
        for barx in bars:
            yval = barx.get_height()
            plt.text(
                barx.get_x() + barx.get_width() / 2,
                yval,
                f"{yval:.2e} kg",
                ha="center",
                va="bottom",
            )  # Using scientific notation
        plt.ylabel(ylabel)
        plt.title("Absolute uncertainty contributions k=1")
        plt.show()

    def present_mass_correction_table(self):
        """
        Creates a visual table showing the measured mass, corrections, and uncertainties combined in a single column.
        The values utilized are collected from the class using .self.
        Parameters:
            - None

        Returns:
            - None
        """
        # Calculate the combined uncertainty using quadrature
        total_uncertainty = (self.vent_abs_unc**2 + self.dv_abs_unc**2) ** 0.5
        # Data to be presented in the table, with uncertainties integrated into the values
        data = [
            ["Measured Mass", f"{self.mass_uncorrected:.3f} kg", ""],
            ["Dead Volume Error", f"{0} kg", f"± {0:.2%}"],
            [
                "Vent Volume Error",
                f"{self.vented_error:.3f} kg",
                f"± {(self.vent_abs_unc/self.vented_error)*100:.2%}",
            ],
            [
                "Corrected Mass",
                f"{self.mass_corrected:.3f} kg",
                f"± {(total_uncertainty/self.mass_corrected)*100:.2%}",
            ],
        ]
        # Column headers
        column_labels = [
            "Parameter",
            "Value (kg)",
            "Associated Relative uncetainty(%), k=1",
        ]
        fig, ax = plt.subplots(figsize=(10, 5))  # Adjust figure size as needed
        ax.axis("tight")
        ax.axis("off")
        ax.set_frame_on(False)  # Remove frame, optional
        # Adjust margins
        plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)
        table = ax.table(
            cellText=data,
            colLabels=column_labels,
            loc="center",
            cellLoc="center",
            colWidths=[0.4, 0.5, 0.5],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)  # Adjust font size for better readability
        table.scale(1, 1.5)
        plt.title(
            "Mass Measurement Correction and Uncertainty Table", pad=20, fontsize=14
        )  # Add padding around the title
        plt.show()

    def plot_uncertainty_contributions(self):
        """
        Plots the relative uncertainties from the filling process over a logarytgmic y-axis.
        The uncertainties plotted are collected from the class parameters.

        Parameters:
            - None

        Returns:
            - None
        """
        plt.figure(figsize=(12, 8))
        # Set up the colors to maintain consistency.
        colors = ["blue", "crimson", "magenta", "yellowgreen"]
        labels = [
            "CFM Contribution",
            "Temperature Contribution",
            "Pressure Contribution",
            "Long-term drift Contribution",
        ]
        lines = ["-", "-", "-", "-"]

        # Plot data with the chosen parameters above
        for data, color, label, line in zip(
            [
                self.rel_cfm_uncs,
                self.rel_temp_conts,
                self.rel_pres_conts,
                self.rel_ltd_conts,
            ],
            colors,
            labels,
            lines,
        ):
            plt.plot(
                self.flowrate_kgmin_per_second,
                data,
                label=label,
                linestyle=line,
                color=color,
                marker="",
                linewidth=2,
            )

        plt.yscale("log")  # Set log y axis
        plt.title("Relative Uncertainty Contributions Across Different Flowrates")
        plt.xlabel("Flowrate (kg/min)")
        plt.ylabel(
            "Relative Uncertainty(%)(log scale)"
        )  # Presiser at skalaen er logaritmisk i y-aksen label
        plt.legend()
        plt.grid(
            True, which="both", linestyle="--", linewidth=0.5
        )  # Tilpass gridlinjene for bedre lesbarhet
        plt.show()

    def plot_simulation_variables(self):
        """
        Plots the simulated flowrate, pressure, and temperature based on the
        fueling protcol. The uncertainties are collected from the class parameters.

        Parameters:
            - None

        Returns:
            -None
        """
        plt.rcParams.update({"font.size": 14})
        fig, ax1 = plt.subplots()
        color = "tab:red"
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Flowrates (kg/sec)", color=color)
        ax1.plot(self.flowrate_kgmin_per_second, color=color)
        ax1.tick_params(axis="y", labelcolor=color)
        ax1.set_ylim([0, max(self.flowrate_kgmin_per_second) * 1.1])

        # Pressures
        ax2 = ax1.twinx()
        color = "tab:blue"
        ax2.set_ylabel("Pressures  (bar)", color=color)
        ax2.plot(self.pressures, color=color)
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylim(
            [min(self.pressures) * 0.9, max(self.pressures) * 1.1]
        )  # Give some headroom

        # Temperature
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(
            ("axes", 1.2)
        )  # This offsets the temperature axis
        color = "tab:green"
        ax3.set_ylabel("Temperature (°C)", color=color)
        ax3.plot(self.temperatures, color=color)
        ax3.tick_params(axis="y", labelcolor=color)
        fig.tight_layout()
        plt.title("Flowrates, Pressures, and Temperature vs. Time")
        plt.show()

    def plot_combined_rel_simulation(self):
        """
        Plots the flowrate against the combined relative uncertainties. Linear interpolation is
        performed between the relative uncertainties, and subsequently hid. The values are
        collected from class parameters.

        Parameters:
            - None

        Returns:
            - None
        """
        flowrate_kg_sec = np.array(
            self.flowrates_kg_sec,
        )
        uncertainties_kg_sec_relative = np.array(self.comb_rel_unc_k)

        # Konverter kg/sec til kg/min
        flowrate_kg_min = flowrate_kg_sec * 60
        n = 1  # Distance between each linear interpolation
        flowrate_thinned = flowrate_kg_min[::n]
        uncertainties_thinned = uncertainties_kg_sec_relative[::n]

        plt.figure(figsize=(10, 5))
        # Can set alpha to 1 to see measured points
        plt.scatter(
            flowrate_thinned,
            uncertainties_thinned,
            color="blue",
            label="Measured Uncertainty",
            s=10,
            alpha=0,
        )
        plt.scatter(
            flowrate_thinned, -uncertainties_thinned, color="blue", s=10, alpha=0
        )
        # Linear interpolation
        if len(flowrate_thinned) > 1:
            sort_index = np.argsort(flowrate_thinned)
            x_sorted = flowrate_thinned[sort_index]
            y_sorted = uncertainties_thinned[sort_index]

            plt.plot(x_sorted, y_sorted, "k--", label="Upper Bound Interpolation")
            plt.plot(x_sorted, -y_sorted, "k--", label="Lower Bound Interpolation")
        plt.title("Flowrate vs Combined Relative Uncertainty")
        plt.xlabel("Flowrate (kg/min)")
        plt.ylabel(f"Relative Uncertainty (%), k={self.k}")
        plt.grid(True)
        plt.axhline(0, color="red", linewidth=0.5)  # Zero line for reference
        plt.legend()
        plt.show()

    def present_mass_data(self, k):
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

        # Calculates total uncertainty: CFM(cfm+p+t+ad))  + DV + Vent
        self.total_relative_fill_unc_k = (
            self.uncertainty_tools.calculate_total_system_rel_unc_k(
                self.mass_corrected,
                self.abs_cfm_uncertainties_std,
                self.correction.pre_fill_pressure,
                self.correction.pre_fill_temp,
                self.correction.post_fill_pressure,
                self.correction.post_fill_temp,
                k,
            )
        )
        # Prints results.
        print("Total mass delivered (before correction):", self.mass_uncorrected, "kg")
        print(
            f"Total mass delivered (after correction): {self.mass_corrected}kg ± {self.total_relative_fill_unc_k} %, k={k}"
        )
        data = [
            [
                "Total mass delivered (after correction)",
                f"{self.mass_corrected:.3f} kg ± {self.total_relative_fill_unc_k:.1f} %",
            ]
        ]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis("tight")
        ax.axis("off")
        table = ax.table(
            cellText=data,
            colLabels=["Description", "Value"],
            cellLoc="center",
            loc="center",
        )
        table.auto_set_font_size(True)
        table.set_fontsize(12)
        table.scale(1.5, 1.5)
        plt.subplots_adjust(left=0.2, right=0.8, top=0.6, bottom=0.4)
        plt.show()

    def create_pie_charts(self, zoom_threshold):
        """
        Create a pie chart, where ecah total relative ucnertainty is shown as a percentage
        relative to the total relative uncertainty. These uncertainties are shown as two pie
        charts, one showing the largest uncertainties, and one highlighting the smallest.

        Parameters:
            - Zoom_threshhold: The maximum size to not include in the largeest pie chart.

        Returns:
            - None

        Note:
            - This presentation was developed in cooperation with an AI (chat-gpt).

        """
        values = [
            self.tot_rel_temp,
            self.tot_rel_pres,
            self.tot_rel_ltd,
            self.tot_rel_vent,
            self.tot_rel_cfm,
        ]  # rel_dv, rel_cfm]
        # Calculate the total to determine the threshold for 'small' and 'large' slices.
        total = sum(values)
        small_slices_threshold = total * zoom_threshold

        custom_colors = [
            "crimson",
            "magenta",
            "yellowgreen",
            "springgreen",
            "royalblue",
        ]  # "darkorange", "royalblue"]
        labels = [
            "Temperature Uncertainty",
            "Pressure Unc",
            "Long-term drift Unc",
            "Vented Unc",
            "CFM Uncertainty",
        ]  #'Dead Volume Uncertainty', 'CFM Uncertainty']
        fig, ax = plt.subplots(1, 2, figsize=(14, 7))

        # Determine which labels to display in the left pie
        large_labels = [
            label if value >= small_slices_threshold else ""
            for label, value in zip(labels, values)
        ]
        pie_chart_radius = 1.0
        # Left pie chart
        wedges, texts, autotexts = ax[0].pie(
            values,
            labels=large_labels,
            autopct=lambda p: (
                f"{p:.1f}%" if (p / 100 * total) >= small_slices_threshold else ""
            ),
            startangle=90,
            colors=custom_colors,
            radius=pie_chart_radius,
        )
        ax[0].set_title("Total Relative Uncertainty, k=1")
        # Manually adjust position of "Dead Volume Uncertainty" label.
        for text, label in zip(texts, labels):
            if label == "Dead Volume Uncertainty":
                text.set_horizontalalignment("right")
                text.set_position(
                    (text.get_position()[0] * 1.1, text.get_position()[1])
                )
        # Quarter view pie chart for small slices (similar size)
        small_values = [value for value in values if value < small_slices_threshold]
        small_labels = [
            label
            for label, value in zip(labels, values)
            if value < small_slices_threshold
        ]
        if small_values:
            ax[1].pie(
                small_values,
                labels=small_labels,
                autopct=lambda p: f"{p * sum(small_values) / total:.2f}%",
                startangle=90,
                radius=pie_chart_radius,
                colors=custom_colors,
            )
            ax[1].set_title("Detailed View of Minor Uncertainties")
        else:
            ax[1].text(
                0.5,
                0.5,
                "No minor uncertainties to display",
                horizontalalignment="center",
                verticalalignment="center",
            )
            ax[1].set_title("Detailed View of Minor Uncertainties")
            ax[1].axis("off")
        plt.tight_layout()
        plt.show()


program = PresentData()
program.run_simulation(1)
# CONFIDENCE INTERVAL CALCULATOR
