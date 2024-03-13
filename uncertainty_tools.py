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

from collect_data import CollectData


class UncertaintyTools:
    """
    A class containing methods for uncertainty calculation and manipulation.
    """

    def __init__(self):
        """
        Initialize UncertaintyTools object.
        """
        self.k = 2
        self.calibraiton_reference_std = None
        self.calibration_repeatability_std = None
        self.calibration_deviation_std = None
        self.field_repeatability_std = None
        self.field_condition_std = None
        self.std_uncertainty_zo_m_factor = 0.0261
        self.flowrate_kg_min = None   

    def gather_data(self):
        """
        Reads data from an Excel sheet using the CollectData class.
        It retrieves calibration and field data, as well as HRS dimensions
        from three seperate sheets. 
        Args:
            None
        Returns:
            None
        """
        data_reader = CollectData()
        data_reader.read_file()

        calibration_data = data_reader.get_calibration_data()

        self.flowrate_kg_min = calibration_data["Flowrate [kg/hr]"]
        self.calibration_deviation_std = calibration_data[
            "Calibration Deviation u(cal,dev)"
        ]
        self.calibration_repeatability_std = calibration_data[
            "Calibration Repeatability u(cal,rept)"
        ]
        self.calibraiton_reference_std = calibration_data[
            "Calibration Reference u(cal,ref)"
        ]

        field_data = data_reader.get_field_data()
        self.field_repeatability_std = field_data["Field Repeatability u(field,rept)"]
        self.field_condition_std = field_data["Field Condition u(field,cond)"]
        # self.field_data = data_reader.get_field_data()


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
        #print("flowrate:", flowrate, "self.flowrate_kg_min:", self.flowrate_kg_min, "uncertainty:", uncertainty)
        return np.interp(flowrate, self.flowrate_kg_min, uncertainty)

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

        return self.linear_interpolation(flowrate, self.field_condition_std)

    def get_field_repeatability_std(self, flowrate):
        """
        Retrieve the interpolated field repeatability standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the field repeatability standard 
            uncertainty.

        Returns:
            float: The interpolated field repeatability standard uncertainty.
        """
        return self.linear_interpolation(flowrate, self.field_repeatability_std)


    def get_calibration_deviation_std(self, flowrate):
        """
        Retrieve the interpolated calibration deviation standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the calibration deviation standard 
            uncertainty.

        Returns:
            float: The interpolated calibration deviation standard uncertainty.
        """
        return self.linear_interpolation(flowrate, self.calibration_deviation_std)


    def get_calibration_reference_std(self, flowrate):
        """
        Retrieve the interpolated calibration reference standard uncertainty for the given flowrate.

        Args:
            flowrate (float): The flowrate for which to retrieve the calibration reference standard 
            uncertainty.

        Returns:
            float: The interpolated calibration reference standard uncertainty.
        """
        return self.linear_interpolation(flowrate, self.calibraiton_reference_std)


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
        return self.linear_interpolation(flowrate, self.calibration_repeatability_std)


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

        calibration_deviation_interp = self.get_calibration_deviation_std(flowrate)
        calibration_repeatability_interp = self.get_calibration_repeatability_std(
            flowrate
        )
        calibration_reference_interp = self.get_calibration_reference_std(flowrate)
        field_repeatability_interp = self.get_field_repeatability_std(flowrate)
        field_condition_interp = self.get_field_condition_std(flowrate)

        var = self.calculate_sum_variance(
            calibration_deviation_interp,
            calibration_repeatability_interp,
            calibration_reference_interp,
            field_condition_interp,
            field_repeatability_interp,
        )
        return self.convert_std_to_confidence(var)


#def run():
    # uncertainty = UncertaintyTools().calculate_relative_uncertainty(flowrate)
    # print(uncertainty)
    # unc = UncertaintyTools()
    #unc.gather_data()
