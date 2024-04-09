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


class UncertaintyTools:
    """
    A class containing methods for uncertainty calculation and manipulation.
    """

    def __init__(self, hrs_config: HRSConfiguration):
        """
        Initialize UncertaintyTools object.
        """
        self.flow_properties = FlowProperties()
        self.hrs_config = hrs_config
        self.k = 2
        self.std_uncertainty_zo_m_factor = 0.0261

    def convert_std_to_confidence(self, std_uncertainty):
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
        return self.k * std_uncertainty

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
            return self.linear_interpolation(
                flowrate, self.hrs_config.get_field_condition()
            )
        else:
            return self.hrs_config.get_field_condition()

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
            return self.linear_interpolation(
                flowrate, self.hrs_config.get_field_repeatability()
            )
        else:
            return self.hrs_config.get_field_repeatability()

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
            return self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_deviation()
            )
        else:
            return self.hrs_config.get_calibration_deviation()

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
            return self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_reference()
            )
        else:
            return self.hrs_config.get_calibration_reference()

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
            return self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_repeatability()
            )
        else:
            return self.hrs_config.get_calibration_repeatability()

    def total_combined_uncertainty(self, time_increments, uncertaintyarray):
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
        return sum(uncertainty * time_increments for uncertainty in uncertaintyarray)

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
        return math.sqrt((uqm / qm) ** 2 + (uz0m / z0m) ** 2) * qvo

    def calculate_relative_uncertainty(self, flowrate):
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
        return self.convert_std_to_confidence(var)
    
    def calculate_density_uncertainty(self, current_pressure, current_temperature):
        """
        ..Absolutt?
        Calculates the density uncertainty based off: (n * m) / V, where n is the ideal
        gas law. Utilizes propagation of uncertainty and partial derivation to reach
        the uncetainty.

        Parameters:
            - Pressure
            - Temperature
        
        Returns:
            - Density uncertainty
        """
        uncertainty_pressure = self.hrs_config.pressure_sensor_uncertainty
        uncertainty_temperature = self.hrs_config.temperature_sensor_uncertainty
        vent_volume = self.hrs_config.depressurization_vent_volume
        vent_uncertainty = self.hrs_config.depressurization_vent_volume_uncertainty
        dn_dp = (vent_volume/(self.flow_properties.gas_constant_r*current_temperature))*uncertainty_pressure**2
        dn_dv = (current_pressure/(self.flow_properties.gas_constant_r*current_temperature))*vent_uncertainty**2
        dn_dt = (current_pressure*vent_volume/(self.flow_properties.gas_constant_r*current_temperature**2))*uncertainty_temperature**2
        uncertainty_n = math.sqrt(dn_dp+dn_dv+dn_dt)

        # Finner så usikkerheten til tetthet. dp_dm er 0, siden usikkerheten til den er nær null.?
        n = (current_pressure * vent_volume ) / (self.flow_properties.gas_constant_r*current_temperature)
        dp_dn = (self.flow_properties.molar_mass_m / vent_volume)*uncertainty_n**2
        dp_dv = (self.flow_properties.molar_mass_m*n/(vent_volume**2))**2
        return math.sqrt(dp_dn+dp_dv)
    
    def calculate_depress_uncertainty(self, pressure, temperature):
        """
        Calculates the uncertainty of the depressurization. The mass depressurized
        is vented to the environment, and is consecutively given as M = p*V

        Parameters:
            - Pressure
            - Temperature

        Returns:
            - Uncertainty of the mass depressurized
        """

        vent_volume = self.hrs_config.depressurization_vent_volume
        vent_uncertainty = self.hrs_config.depressurization_vent_volume_uncertainty
        density = self.flow_properties.calculate_hydrogen_density(pressure, temperature, vent_volume)
        density_uncertainty = self.calculate_density_uncertainty(pressure, temperature)

        dm_dp = (vent_volume*density_uncertainty)**2
        dm_dv = (density* vent_uncertainty)**2
        return math.sqrt(dm_dp+ dm_dv)


# def run():
# uncertainty = UncertaintyTools().calculate_relative_uncertainty(flowrate)
# print(uncertainty)
# unc = UncertaintyTools()
# unc.gather_data()
