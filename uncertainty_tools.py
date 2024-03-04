import numpy as np
from collect_data import CollectData as data

import pandas as pd
import math

# TODO: Få kontroll på enheter
# TODO: Få kontroll på usikkerhetsintervall. Kva er u_std, ka er u_95%


class UncertaintyTools:
    def __init__(self):
        self.k = 2
        self.calibraiton_reference_std = None
        self.calibration_repeatability_std = None
        self.calibration_deviation_std = None
        self.field_repeatability_std = None
        self.field_condition_std = None
        self.std_uncertainty_zo_m_factor = 0.0261
        self.flowrate_kg_min = None

    # Idemyldring.
    # Vurdere en egen klasse her som samler inn data? Evt fra notatblokk? Excel ark?
    # La oss si nokken skal bruke programmet, kor skal dei legge inn verdiane?
    # Kanskje lage en 'excel' mal for å legge inn tall, den leser og legger alt inn her.

    def gather_data(self):
        data_reader = data()
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

    ##################################################################################################################################
    # Uncertainty tools
    #################################################################################################################################

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
        Performs linear interpolation on data using NumPy's 'interp' function.
        Args:
            flowrate (float): The flowrate value for which to interpolate uncertainty.
            uncertainty (array-like): The uncertainty data corresponding to the flowrates_kg_hr array.
        Returns:
            float: The interpolated value for the given flowrate.
        """
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

    ##################################################################################################################################
    # Field uncertainty
    #################################################################################################################################

    def get_field_condition_std(self, flowrate):
        return self.linear_interpolation(flowrate, self.field_condition_std)

    def get_field_repeatability_std(self, flowrate):
        return self.linear_interpolation(flowrate, self.field_repeatability_std)

    ##################################################################################################################################
    # Calibration uncertainty
    #################################################################################################################################

    def get_calibration_deviation_std(self, flowrate):
        return self.linear_interpolation(flowrate, self.calibration_deviation_std)

    def get_calibration_reference_std(self, flowrate):
        return self.linear_interpolation(flowrate, self.calibraiton_reference_std)

    def get_calibration_repeatability_std(self, flowrate):
        return self.linear_interpolation(flowrate, self.calibration_repeatability_std)

    ################################################################################################
    # Combining uncertainty
    ################################################################################################
    def total_combined_uncertainty(self, time_increments, uncertaintyarray):
        return sum(uncertainty * time_increments for uncertainty in uncertaintyarray)

    ################################################################################################
    # Flow calculation uncetainty
    ################################################################################################
    def calculate_std_vol_flowrate_uncertainty(self, qvo, qm, uqm, z0m, uz0m):
        return math.sqrt((uqm / qm) ** 2 + (uz0m / z0m) ** 2) * qvo

    def calculate_relative_uncertainty(self, flowrate):
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


def run(flowrate):
    # uncertainty = UncertaintyTools().calculate_relative_uncertainty(flowrate)
    # print(uncertainty)
    unc = UncertaintyTools()
    unc.gather_data()
