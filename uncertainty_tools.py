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
        self.std_uncertainty_zo_m_factor = 0.0261

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
        """
        Converts relative uncertainty to absolute uncertainty.

        Parameters:
            - Relative uncertainty (%)
            - Reference measurement (unit)

        Returns:
            - Absolute uncertainty (unit)
        """
        absolute_uncertainty = (uncertainty) * reference
        return absolute_uncertainty

    def get_field_condition_std(self, flowrate):
        """
        Retrieve the interpolated field condition standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the field condition standard
            uncertainty.

        Returns:
            float: The interpolated field condition standard uncertainty for the given
            flowrate [kg/min].
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
            float: The interpolated field repeatability standard uncertaint [kg/min].
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
            uncertainty [kg/min].

        Returns:
            float: The interpolated absolute calibration deviation standard uncertainty [kg/min]
        """
        if self.hrs_config.multiple_calibration_deviation_bool:
            relative_uncertainty = self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_deviation()
            )
        else:
            relative_uncertainty = self.hrs_config.get_calibration_deviation()
        # print(f"relative_cal_dev uncertainty: {relative_uncertainty}")
        return self.convert_relative_to_absolute(relative_uncertainty, flowrate)

    def get_calibration_reference_std(self, flowrate):
        """
        Retrieve the interpolated calibration reference standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the calibration reference standard
            uncertainty.

        Returns:
            float: The interpolated absolute calibration reference standard uncertainty [kg/min].
        """
        if self.hrs_config.multiple_calibration_reference_bool:
            # print(self.hrs_config.get_calibration_reference())
            reltive_uncertainty = self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_reference()
            )
        else:
            reltive_uncertainty = self.hrs_config.get_calibration_reference()
        # print(f"relative_cal_dev uncertainty: {reltive_uncertainty}")
        return self.convert_relative_to_absolute(reltive_uncertainty, flowrate)

    def get_calibration_repeatability_std(self, flowrate):
        """
        Retrieve the interpolated calibration repeatability standard uncertainty for the given
        flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the calibration repeatability
            standard uncertainty.

        Returns:
            float: The interpolated calibration repeatability standard uncertainty [kg/min]
        """
        if self.hrs_config.multiple_calibration_repeatability_bool:
            unc_rel = self.linear_interpolation(
                flowrate, self.hrs_config.get_calibration_repeatability()
            )
            return self.convert_relative_to_absolute(unc_rel, flowrate)
        else:
            return self.hrs_config.get_calibration_repeatability()

    def calculate_total_combined_unc(self, uncertainties_abs_std, format):
        """
        Calculate the total combined uncertainty.

        Args:
            - uncertainties_abs_std: Array containing absolute uncertainties [kg/min] per second.

        Returns:
            - Uncertainty_mass: The total combined uncertainty of mass measured by the CFM [kg].
        """
        uncertainty_mass = 0
        for uncertainty in uncertainties_abs_std:
            uncertainty_mass += uncertainty * format
        return uncertainty_mass

    def calculate_std_vol_flowrate_unc(self, qvo, qm, uqm, z0m, uz0m):
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

    def calculate_cfm_abs_unc_std(self, flowrate):
        """
        Calculate the CFM absolute uncertainty of the current flowrate.

        This method calculates the relative uncertainty of the flowrate measurement based on
        the provided flowrate value. It retrieves interpolated uncertainties for calibration
        deviation, calibration repeatability, calibration reference, field repeatability,
        and field condition, and then calculates the sum of variances using these uncertainties.

        Args:
            flowrate (float): The flowrate for which to calculate the relative uncertainty.

        Returns:
            float: The absolute standard uncertainty of the flowrate measurement [kg/min].
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
            field_repeatability)
        return var
    
    def calculate_total_abs_unc_std(self, flowrate, temperature, pressure):
        """
        Calculate the CFM absolute uncertainty of the current flowrate.

        This method calculates the relative uncertainty of the flowrate measurement based on
        the provided flowrate value. It retrieves interpolated uncertainties for calibration
        deviation, calibration repeatability, calibration reference, field repeatability,
        and field condition, and then calculates the sum of variances using these uncertainties.

        Args:
            flowrate (float): The flowrate for which to calculate the relative uncertainty.

        Returns:
            float: The absolute standard uncertainty of the flowrate measurement [kg/min].
        """
        if flowrate == 0:
            return 0

        calibration_deviation = self.get_calibration_deviation_std(flowrate)
        calibration_repeatability = self.get_calibration_repeatability_std(flowrate)
        calibration_reference = self.get_calibration_reference_std(flowrate)
        field_repeatability = self.get_field_repeatability_std(flowrate)
        field_condition = self.get_field_condition_std(flowrate)

        # print(f"flowrate: {flowrate}, temp: {temperature}, pres: {pressure}")

        # Henter absolutt verdi for temp, konverterer rel trykk og årlig deviasjon.
        abs_temp = self.calculate_abs_temp_per_sample(temperature)
        abs_pres =  self.calculate_absolute_pressure_unc(pressure, flowrate)
        abs_annual = self.calculate_absolute_annual_dev(flowrate)
        print(f"abs_temp_cont: {abs_temp} kg/s, abs_pres_cont: {abs_pres} kg/s, abs_annual: {abs_annual} kg/s \n")

        var = self.calculate_sum_variance(
            calibration_deviation,
            calibration_repeatability,
            calibration_reference,
            field_condition,
            field_repeatability,
            abs_temp,
            abs_pres,
            abs_annual,
        )
        return var


    def calculate_cfm_rel_unc_95(self, flowrate, temperature, pressure, k):
        """
        Calculate the relative uncertainty of the CFM to the current flowrate.

        This method calculates the relative uncertainty of the flowrate measurement based on
        the provided flowrate value. It retrieves interpolated uncertainties for calibration
        deviation, calibration repeatability, calibration reference, field repeatability,
        and field condition, and then calculates the sum of variances using these uncertainties.
        Based on NFOGM gas metering handbook.

        Args:
            flowrate (float): The flowrate for which to calculate the relative uncertainty [kg/min]

        Returns:
            float: The relative uncertainty of the flowrate measurement.
        """
        if flowrate == 0:
            return 0
        calibration_deviation = (
            self.get_calibration_deviation_std(flowrate) / flowrate
        ) * 100
        calibration_repeatability = (
            self.get_calibration_repeatability_std(flowrate) / flowrate
        ) * 100
        calibration_reference = (
            self.get_calibration_reference_std(flowrate) / flowrate
        ) * 100
        field_repeatability = (
            self.get_field_repeatability_std(flowrate) / flowrate
        ) * 100
        field_condition = (self.get_field_condition_std(flowrate) / flowrate) * 100

        temp_unc =  self.calculate_relative_temperature_uncertainty(flowrate, temperature)
        press_unc =  self.calculate_relative_pressure_uncertainty(pressure)
        annual_dev_unc = self.calculate_relative_annual_dev()

        # print(
        #    calibration_deviation,
        #    calibration_repeatability,
        #    calibration_reference,
        #    field_repeatability,
        #    field_condition,
        # )
        var = self.calculate_sum_variance(
            calibration_deviation,
            calibration_repeatability,
            calibration_reference,
            field_condition,
            field_repeatability,
            temp_unc,
            press_unc,
            annual_dev_unc,
        )
        # print(f"relative var= {var}")
        return self.convert_std_to_confidence(var, k)

    def calculate_density_abs_unc_std(self, pressure, temperature):
        """
        Calculates the density uncertainty based off: (n * m) / V, where n is the ideal
        gas law. Utilizes propagation of uncertainty and partial derivation to reach
        the uncetainty.

        Parameters:
            - Pressure [Pa]
            - Temperature [K]

        Returns:
            - Density uncertainty [kg/m3]
        """
        unc_pressure_abs = self.hrs_config.get_pressure_uncertainty(pressure)
        unc_temp_abs = self.hrs_config.get_temperature_uncertainty(
            temperature
        )
        m = self.flow_properties.molar_mass_m
        r = self.flow_properties.gas_constant_r
        drho_dp = (m)/(r*temperature)
        drho_dt = (pressure*m)/(r*temperature**2)
        return self.calculate_sum_variance((drho_dp*unc_pressure_abs),(drho_dt*unc_temp_abs))

    def calculate_depress_abs_unc(self, pressure, temperature):
        """
        Calculates the uncertainty of the depressurization. The mass depressurized
        is vented to the environment, and is consecutively given as M = p*V.
        The uncertainty calculation is found by utilizing error propagation by
        partial derivation.

        Parameters:
            - Pressure [Pa]
            - Temperature [Kelvin]

        Returns:
            - Uncertainty of the mass depressurized [kg]
        """

        vent_volume = self.hrs_config.get_depressurization_vent_volume()  # 0.0025 m3
        vent_uncertainty = self.hrs_config.get_depressurization_vent_volume_unc()
        density = self.flow_properties.calculate_hydrogen_density(pressure, temperature)
        density_uncertainty = self.calculate_density_abs_unc_std(pressure, temperature)
        dm_dp = vent_volume
        dm_dv = density
        return self.calculate_sum_variance(
            (dm_dp * density_uncertainty), (dm_dv * vent_uncertainty)
        )

    def caclulate_dead_volume_abs_unc(self, pre_press, pre_temp, post_press, post_temp, volume=None):
        """
        Calculates the dead volume uncertainty based on partial derivation and error
        propagation.

        Args:
            - Pre-fill-pressure: Previous filling pressure [Pa]
            - Pre-fill-temperature: Previous filling temperature [K]
            - Post-fill-pressure: Current filling pressure [Pa]
            - Post-fil-temperature: Current filling temperature [K]
        """
        if volume is None:
            dead_volume = self.hrs_config.get_dead_volume()
        else:
            dead_volume = volume
        dead_volume_unc = self.hrs_config.get_dead_volume_uncertainty()

        prev_density = self.flow_properties.calculate_hydrogen_density(pre_press, pre_temp)
        current_density = self.flow_properties.calculate_hydrogen_density(post_press, post_temp)

        prev_density_unc = self.calculate_density_abs_unc_std(pre_press, pre_temp)
        current_density_unc = self.calculate_density_abs_unc_std(post_press, post_temp)

        dm_dv = current_density - prev_density
        dm_p2 = dead_volume
        dm_p1 = dead_volume
        return self.calculate_sum_variance(
            (dm_dv * dead_volume_unc),
            (dm_p1 * prev_density_unc),
            (dm_p2 * current_density_unc),
        )

    def calculate_total_system_rel_unc_95(
        self,
        mass_delivered,
        uncertainties,
        pre_fill_press,
        pre_fill_temp,
        post_fill_press,
        post_fill_temp,
        k,
    ):
        """
        This method calculates the total uncertainty to the mass correction, given in relative
        expanded uncertainty, for k = 2. It uses three methods to calculate it. CFM uncertainty
        returns totaled uncertainty from measurements, in kg.Mass vented uncertainty in kg, and
        the uncertainty in change in mass from dead volume in kg.

        Parameters:
            - Mass delivered: Calculated corrected mass delivered [kg]
            - Uncertainties: CFM absolute std uncertainties [kg/min]
            - Pre-fill-pressure: Previous filling pressure [Pa]
            - Pre-fill-temperature: Previous filling temperature [K]
            - Post-fill-pressure: Current filling pressure [Pa]
            - Post-fil-temperature: Current filling temperature [K]

        """
        cfm_uncertainty = self.calculate_total_combined_unc(uncertainties, 1/60)
        # -> Returnerer kalkulert abs suikkerhet til CFM målinger [kg].

        depress_vent_uncertainty = self.calculate_depress_abs_unc(
            post_fill_press, post_fill_temp
        )
        # -> Returnerer kalkulert abs usikkerhet til depress [kg]

        dead_volume_uncertainty = self.caclulate_dead_volume_abs_unc(
            pre_fill_press,
            pre_fill_temp,
            post_fill_press,
            post_fill_temp,
        )
        # -> returnerer kalkulert abs usikkerhet til dødvolum [kg]

        print(
            f"CFM uncertainty: {cfm_uncertainty}kg    Depressurized vent uncertainty: {depress_vent_uncertainty}kg  Dead volume uncertainty: {dead_volume_uncertainty}kg"
        )

        rel_unc = self.calculate_sum_variance(
            (cfm_uncertainty / mass_delivered) * 100,
            (depress_vent_uncertainty / mass_delivered) * 100,
            (dead_volume_uncertainty / mass_delivered) * 100,
        )

        expanded_relative_uncertainty = self.convert_std_to_confidence(rel_unc, k)
        return expanded_relative_uncertainty

    def return_total_system_rel_uncs(
        self, mass_delivered, cfm_uncertainties, dvs, vvs, tts, pps, ans, k
    ):
        """
        Eh.
        """
        #print(mass_delivered, cfm_uncertainties, dvs, vvs, tts, pps, ans)
        cfm_uncertainty = self.calculate_total_combined_unc(cfm_uncertainties, 1 / 60)

        tt_unc = self.calculate_total_combined_unc(tts, 1)
        pp_unc = self.calculate_total_combined_unc(pps, 1)
        an_unc = self.calculate_total_combined_unc(ans, 1)
        #print(f"total tt : {tt_unc} kg")
        #print(f"total pp: {pp_unc} kg")

        rel_tt = (tt_unc / mass_delivered) * 100
        rel_pp = (pp_unc / mass_delivered) * 100
        rel_an = (an_unc / mass_delivered) * 100
        rel_vv = (vvs / mass_delivered) * 100
        rel_dv = (dvs / mass_delivered) * 100
        rel_cfm = (cfm_uncertainty / mass_delivered) * 100
        var = self.calculate_sum_variance(rel_tt, rel_pp, rel_cfm, rel_an, rel_vv, rel_dv)
        #print(f"vars: {var}")

        return rel_tt, rel_pp, rel_an, rel_vv, rel_dv, rel_cfm
    
    def return_total_system_abs_uncs(
        self, cfm_uncertainties, tts, pps, ans, k):
        """
        Eh.
        """
        #print(mass_delivered, cfm_uncertainties, dvs, vvs, tts, pps, ans)
        cfm_uncertainty = self.calculate_total_combined_unc(cfm_uncertainties, 1 / 60)

        tt_unc = self.calculate_total_combined_unc(tts, 1)
        pp_unc = self.calculate_total_combined_unc(pps, 1)
        an_unc = self.calculate_total_combined_unc(ans, 1)
        return tt_unc, pp_unc, an_unc, cfm_uncertainty

    def calculate_relative_pressure_uncertainty(self, pressure):
        """
        Returns the relative uncertainty associated to increasing pressure.

        Parameters:
            - Pressure [bars]

        Return:
            - Relative uncertainty associated to pressure.
        """
        return self.hrs_config.pressure_contribution * pressure * (-1)

    def calculate_absolute_pressure_unc(self, pressure, flowrate):
        rel_pres_cont = self.calculate_relative_pressure_uncertainty(pressure)
        abs_pres_cont = (rel_pres_cont / 100) * (flowrate / 60)
        return abs_pres_cont

    def calculate_abs_temp_per_sample(self, temperature):
        prev_temp = self.hrs_config.previous_temperature
        if temperature != prev_temp:
            abs_temp_kg_min = self.hrs_config.temperature_contribution  #7.5E-5 kg/min
            abs_temp_kg_s = abs_temp_kg_min / 60  # kg s
        else:
            abs_temp_kg_s = 0
        return abs_temp_kg_s
    
    def calculate_relative_temperature_uncertainty(self, flowrate, temperature):
        """
        Returns the relative uncertainty associated to increasing temperature.
        If this module is to be utilized in a different program, the temp_init
        must be set as the starting temperature.

        Parameters:
            - flowrate [kg/min]
            - Temperature [C]

        Return:
            - Relative uncertainty associated to temperature.
        """
        abs_temp_kg_s = self.calculate_abs_temp_per_sample(temperature)
        rel_unc = (abs_temp_kg_s / flowrate) * 100  # *(-1)
        return rel_unc

    def calculate_relative_annual_dev(self):
        """
        Returns the annual deviation relative uncertainty based on flowrate.

        Parameters:
            - Flowrate [kg/min]
        Returns:
            - Relative uncertainty for current flowrate [%]
        """
        annual_deviation = (
            self.hrs_config.annual_deviation * self.hrs_config.years_since_calibration
        )
        return annual_deviation

    def calculate_absolute_annual_dev(self, flowrate):
        rel_annual_deviation = (
            self.hrs_config.annual_deviation * self.hrs_config.years_since_calibration
        )
        abs_an_dev = (rel_annual_deviation * flowrate) / 100  # kg / min
        abab = abs_an_dev / 60
        return abab

    def return_misc_press_data(self, flowrate, pressure, temperature, k):
        """
        This method returns the relative uncertainty of the pressure, temperature,
        and annual deviation - for plotting purposes.

        """
        rel_temp_unc = self.calculate_relative_temperature_uncertainty(
            flowrate, temperature
        )
        rel_press_unc = self.calculate_relative_pressure_uncertainty(pressure)
        rel_annual_dev_unc = self.calculate_relative_annual_dev()

        abs_temp_unc = self.calculate_abs_temp_per_sample(temperature)
        abs_press_unc = self.calculate_absolute_pressure_unc(pressure, flowrate)
        abs_annual_dev_unc = self.calculate_absolute_annual_dev(flowrate)

        return (
            rel_temp_unc,
            rel_press_unc,
            rel_annual_dev_unc,
            abs_temp_unc,
            abs_press_unc,
            abs_annual_dev_unc,
        )

    def return_abs_error_data(
        self,
        pre_fill_press,
        pre_fill_temp,
        post_fill_press,
        post_fill_temp,
    ):
        """
        Yep.
        """
        depress_vent_uncertainty = self.calculate_depress_abs_unc(
            post_fill_press, post_fill_temp
        )

        # -> Returnerer kalkulert abs usikkerhet til depress [kg]
        dead_volume_uncertainty = self.caclulate_dead_volume_abs_unc(
            pre_fill_press,
            pre_fill_temp,
            post_fill_press,
            post_fill_temp,
        )
        return depress_vent_uncertainty, dead_volume_uncertainty
