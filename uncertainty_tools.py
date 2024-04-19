"""
UncertaintyTools Module

This module provides a collection of tools for uncertainty calculation and manipulation.

Classes:
    UncertaintyTools: A class containing methods for gathering data from an Excel sheet,
                      performing various uncertainty calculations, and more.
                      The main goal of multiple functions is to calculate the uncertainty
                      at a given flowrate, by using reccomended linear interpolation methods.

Functions:
    None
"""

import math
import numpy as np
from hrs_config import HRSConfiguration
from flow_calculations import FlowProperties
from correction import Correction


class UncertaintyTools:
    """
    A class containing methods for uncertainty calculation and manipulation.
    """

    def __init__(self, hrs_config: HRSConfiguration, correction: Correction):
        """
        Initialize UncertaintyTools object.
        """
        self.flow_properties = FlowProperties()
        self.correcter = correction
        self.hrs_config = hrs_config
        self.k = 2
        self.std_uncertainty_zo_m_factor = 0.0261
        self.flowrates_in_g_s = True

    def convert_std_to_confidence(self, std_uncertainty, k):
        """
        Converts standard uncertainty to confidence interval based on coverage factor 'k'.

        Args:
            std_uncertainty (float): The standard uncertainty value.

        Returns:
            float: The confidence interval value.

        Raises:
            ValueError: If the provided std_uncertainty is not a positive number.
        """

        if std_uncertainty <= 0:
            raise ValueError("Standard uncertainty must be a positive number.")
        return k * std_uncertainty

    def linear_interpolation(self, flowrate, uncertainty):
        """
        Performs linear interpolation to estimate uncertainty for a given flowrate.

        Args:
            flowrate (float): The flowrate value for which to perform interpolate.
            uncertainty (array): The uncertainty data corresponding to the flowrates_kg_min array.

        Returns:
            float: The interpolated value for the given flowrate.
        """
        return np.interp(flowrate, self.hrs_config.flowrates_kg_min, uncertainty)

    def calculate_sum_variance(self, *args):
        """
        Calculates the combined variance by summing the squared deviations of provided arguments.

        Args:
            *args: Variable number of arguments representing contributing uncertainties.

        Returns:
            float: The combined variance value.

        Raises:
            ValueError: If no arguments are provided.
        """

        if not args:
            raise ValueError("At least one argument (uncertainty) is required.")

        # Square each argument and sum them
        squared_variances = sum(arg**2 for arg in args)

        # Return the square root of the sum (combined variance)
        return math.sqrt(squared_variances)

    def convert_relative_to_absolute(self, uncertainty, reference):
        absolute_uncertainty = uncertainty * reference#TODO: bdkn gfjewqnf oweangf ojwebgo jwb
        return absolute_uncertainty

    def get_field_condition_std(self, flowrate):
        """
        Retrieve the interpolated field condition standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the field condition standard
            uncertainty.

        Returns:
            float: The interpolated field condition standard uncertainty for the given flowrate.
        """
        if self.hrs_config.multiple_field_condition_bool:
            relative_uncertainty = self.linear_interpolation(
                flowrate, self.hrs_config.get_field_condition()
            )
        else:
            relative_uncertainty = self.hrs_config.get_field_condition()
        return self.convert_relative_to_absolute(relative_uncertainty, flowrate)

    def get_field_repeatability_std(self, flowrate):
        """
        Retrieve the interpolated field repeatability standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the field repeatability standard
            uncertainty.

        Returns:
            float: The interpolated field repeatability standard uncertainty.
        """
        if self.hrs_config.multiple_field_repeatability_bool:
            relative_uncertainty = self.linear_interpolation(
                flowrate, self.hrs_config.get_field_repeatability()
            )
        else:
            relative_uncertainty = self.hrs_config.get_field_repeatability()
        return self.convert_relative_to_absolute(relative_uncertainty, flowrate)

    def get_calibration_deviation_std(self, flowrate):
        """
        Retrieve the interpolated calibration deviation standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the calibration deviation standard
            uncertainty.

        Returns:
            float: The interpolated calibration deviation standard uncertainty.
        """
        if self.hrs_config.multiple_calibration_deviation_bool:
            relative_uncertainty = self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_deviation()
            )
        else:
            relative_uncertainty = self.hrs_config.get_calibration_deviation()
        return self.convert_relative_to_absolute(relative_uncertainty, flowrate)

    def get_calibration_reference_std(self, flowrate):
        """
        Retrieve the interpolated calibration reference standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the calibration reference standard
            uncertainty.

        Returns:
            float: The interpolated calibration reference standard uncertainty.
        """
        if self.hrs_config.multiple_calibration_reference_bool:
            reltive_uncertainty = self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_reference()
            )
        else:
            reltive_uncertainty = self.hrs_config.get_calibration_reference()
        return self.convert_relative_to_absolute(reltive_uncertainty, flowrate)

    def get_calibration_repeatability_std(self, flowrate):
        """
        Retrieve the interpolated calibration repeatability standard uncertainty for the given
        flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the calibration repeatability
            standard uncertainty.

        Returns:
            float: The interpolated calibration repeatability standard uncertainty.
        """
        if self.hrs_config.multiple_calibration_repeatability_bool:
            unc_rel = self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_repeatability()
            )
            return self.convert_relative_to_absolute(unc_rel, flowrate)
        else:
            return self.hrs_config.get_calibration_repeatability()

    def total_combined_uncertainty(self, uncertaintyarray):
        """
        Calculate the total combined uncertainty.

        This method calculates the total combined uncertainty by summing the product
        of each uncertainty value in the uncertainty array and the corresponding time increment.

        Args:
            time_increments (array-like): Array-like object containing time increments.
            uncertaintyarray (array-like): Array-like object containing uncertainty values.

        Returns:
            float: The total combined uncertainty.
        """
        uncertainty_mass = 0
        delta_t = 1  # Since the uncertainty array contains data per second, even though
        # the flowrate is given as kg/min.
        for uncertainty in uncertaintyarray:
            uncertainty_mass += uncertainty * delta_t
        return uncertainty_mass

    def calculate_std_vol_flowrate_uncertainty(self, qvo, qm, uqm, z0m, uz0m):
        """
        Calculate the standard uncertainty for the standard volumetric flow rate.

        Args:
            qvo (float): The standard volumetric flow rate.
            qm (float): The mass flow rate.
            uqm (float): The standard uncertainty of the mass flow rate.
            z0m (float): gas compressibility.
            uz0m (float): The standard uncertainty of gass compressibility.

        Returns:
            float: The standard uncertainty of the volumetric flow rate.
        """
        # TODO: trenge implementasjon
        return math.sqrt((uqm / qm) ** 2 + (uz0m / z0m) ** 2) * qvo

    def calculate_absolute_std_uncertainty_cfm(self, flowrate):
        """
        Calculate the relative uncertainty of the flowrate measurement.

        This method calculates the relative uncertainty of the flowrate measurement based on
        the provided flowrate value. It retrieves interpolated uncertainties for calibration
        deviation, calibration repeatability, calibration reference, field repeatability,
        and field condition, and then calculates the sum of variances using these uncertainties.

        Args:
            flowrate (float): The flowrate for which to calculate the relative uncertainty.

        Returns:
            float: The relative uncertainty of the flowrate measurement.
        """
        if flowrate == 0:
            return 0

        calibration_deviation = self.get_calibration_deviation_std(flowrate)
        calibration_repeatability = self.get_calibration_repeatability_std(flowrate)
        calibration_reference = self.get_calibration_reference_std(flowrate)
        field_repeatability = self.get_field_repeatability_std(flowrate)
        field_condition = self.get_field_condition_std(flowrate)

        var = self.calculate_sum_variance(
            calibration_deviation,
            calibration_repeatability,
            calibration_reference,
            field_condition,
            field_repeatability,
        )
        # print(calibration_deviation, calibration_repeatability, calibration_reference, field_repeatability, field_condition )
        return var  # TODO: Gjør var funksjonen det den skal?

    def calculate_relative_uncertainty_95(self, flowrate, reference):
        """
        Calculate the relative uncertainty of the flowrate measurement.

        This method calculates the relative uncertainty of the flowrate measurement based on
        the provided flowrate value. It retrieves interpolated uncertainties for calibration
        deviation, calibration repeatability, calibration reference, field repeatability,
        and field condition, and then calculates the sum of variances using these uncertainties.
        Based on NFOGM gas metering handbook.

        Args:
            flowrate (float): The flowrate for which to calculate the relative uncertainty.

        Returns:
            float: The relative uncertainty of the flowrate measurement.
        """
        k = 2
        if flowrate == 0:
            return 0

        calibration_deviation = self.get_calibration_deviation_std(flowrate) / reference
        calibration_repeatability = (
            self.get_calibration_repeatability_std(flowrate) / reference
        )
        calibration_reference = self.get_calibration_reference_std(flowrate) / reference
        field_repeatability = self.get_field_repeatability_std(flowrate) / reference
        field_condition = self.get_field_condition_std(flowrate) / reference

        var = self.calculate_sum_variance(
            calibration_deviation,
            calibration_repeatability,
            calibration_reference,
            field_condition,
            field_repeatability,
        )
        """print(
            calibration_deviation,
            calibration_repeatability,
            calibration_reference,
            field_repeatability,
            field_condition,
        )"""
        return self.convert_std_to_confidence(var, k)

    def calculate_density_absolute_uncertainty_std(
        self, pressure, temperature, volume, volume_uncertainty
    ):
        """
        Calculates the density uncertainty based off: (n * m) / V, where n is the ideal
        gas law. Utilizes propagation of uncertainty and partial derivation to reach
        the uncetainty.

        Parameters:
            - Pressure
            - Temperature

        Returns:
            - Density uncertainty
        """
        uncertainty_pressure_abs = self.hrs_config.get_pressure_uncertainty(pressure)
        uncertainty_temperature_abs = self.hrs_config.get_temperature_uncertainty(
            temperature
        )
        # print(f"u(T): {uncertainty_temperature} u(P): {uncertainty_pressure}")

        dn_dp = volume / (self.flow_properties.gas_constant_r * temperature)
        dn_dv = pressure / (self.flow_properties.gas_constant_r * temperature)
        dn_dt = (
            pressure * volume / (self.flow_properties.gas_constant_r * temperature**2)
        )
        uncertainty_n = self.calculate_sum_variance(
            (dn_dp * uncertainty_pressure_abs),
            (dn_dv * volume_uncertainty),
            (dn_dt * uncertainty_temperature_abs),
        )

        # Finner så usikkerheten til tetthet. dp_dm er 0, siden usikkerheten til den er nær null.?
        n = (pressure * volume) / (self.flow_properties.gas_constant_r * temperature)
        dp_dn = self.flow_properties.molar_mass_m / volume
        dp_dv = self.flow_properties.molar_mass_m * n / (volume**2)
        return self.calculate_sum_variance(
            (dp_dn * uncertainty_n), (dp_dv * volume_uncertainty)
        )

    def calculate_depress_absolute_uncertainty(self, pressure, temperature):
        """
        Calculates the uncertainty of the depressurization. The mass depressurized
        is vented to the environment, and is consecutively given as M = p*V.
        The uncertainty calculation is found by utilizing error propagation by
        partial derivation.

        Parameters:
            - Pressure
            - Temperature

        Returns:
            - Uncertainty of the mass depressurized, in kg.
        """

        vent_volume = self.hrs_config.get_depressurization_vent_volume()
        vent_uncertainty = self.hrs_config.get_depressurization_vent_volume_unc()
        density = self.flow_properties.calculate_hydrogen_density(
            pressure, temperature, vent_volume
        )
        density_uncertainty = self.calculate_density_absolute_uncertainty_std(
            pressure, temperature, vent_volume, vent_uncertainty
        )

        dm_dp = vent_volume
        dm_dv = density
        return self.calculate_sum_variance(
            (dm_dp * density_uncertainty), (dm_dv * vent_uncertainty)
        )

    def calculate_total_meter_uncertainty_confidence(self, uncertainties, k):
        cfm_unc = self.total_combined_uncertainty(uncertainties)
        return cfm_unc

    def caclulate_dead_volume_uncertainty_absolute(
        self, pressure2, pressure1, temperature2, temperature1
    ):
        """
        Calculates the uncertainty related to uncertainty, based on partial derivation and error
        propagation.
        """
        dead_volume = self.hrs_config.get_dead_volume()
        dead_volume_unc = self.hrs_config.get_dead_volume_uncertainty()

        prev_density = self.flow_properties.calculate_hydrogen_density(
            pressure1, temperature1, dead_volume
        )
        current_density = self.flow_properties.calculate_hydrogen_density(
            pressure2, temperature2, dead_volume
        )
        prev_density_unc = self.calculate_density_absolute_uncertainty_std(
            pressure1, temperature1, dead_volume, dead_volume_unc
        )
        current_density_unc = self.calculate_density_absolute_uncertainty_std(
            pressure2, temperature2, dead_volume, dead_volume_unc
        )

        dm_dv = current_density - prev_density
        dm_p2 = dead_volume
        dm_p1 = dead_volume
        return self.calculate_sum_variance(
            (dm_dv * dead_volume_unc),
            (dm_p1 * prev_density_unc),
            (dm_p2 * current_density_unc),
        )

    def calculate_total_system_relative_uncertainty_confidence(
        self,
        mass_delivered,
        uncertainties,
        prev_filling_pressure,
        prev_filling_temperature,
        final_filling_pressure,
        final_filling_temperature,
        k,
    ):
        """
        This method calculates the total uncertainty to the mass correction, given in relative expanded uncertainty,
        for k = 2. It uses three methods to calculate it. CFM uncertainty returns totaled uncertainty from measurements, in kg.
        Mass vented uncertainty in kg, and the uncertainty in change in mass from dead volume in kg.
        """
        # TODO: Returnerer total masse usikkerhet
        cfm_uncertainty = self.total_combined_uncertainty(
            uncertainties
        )  # TODO: Antar full positiv korrelasjon - ligning
        depress_vent_uncertainty = self.calculate_depress_absolute_uncertainty(
            final_filling_pressure, final_filling_temperature
        )
        dead_volume_uncertainty = self.caclulate_dead_volume_uncertainty_absolute(
            final_filling_pressure,
            prev_filling_pressure,
            final_filling_temperature,
            prev_filling_temperature,
        )
        print(
            f"CFM uncertainty: {cfm_uncertainty}    Depressurized vent uncertainty: {depress_vent_uncertainty}      Dead volume uncertainty: {dead_volume_uncertainty}"
        )
        rel_unc = self.calculate_sum_variance(
            cfm_uncertainty / mass_delivered,
            depress_vent_uncertainty / mass_delivered,
            dead_volume_uncertainty / mass_delivered,  # TODO: mass_corrected.
        )
        expanded_relative_uncertainty = self.convert_std_to_confidence(rel_unc, k)
        return expanded_relative_uncertainty
