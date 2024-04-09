import numpy as np
import math

# TODO: Få kontroll på enheter
# TODO: Få kontroll på usikkerhetsintervall. Kva er u_std, ka er u_95%


class UncertaintyTools:
    def __init__(self):
        self.k = 2
        self.std_uncertainty_calib_reference = 0.1
        self.std_uncertainty_calib_repeatability = 0.05
        self.std_uncertainty_calib_deviation = 0.145
        self.std_uncertainty_field_repeatability = 0
        self.std_uncertainty_field_conditions = 0
        self.std_uncertainty_zo_m_factor = 0.0261

        self.flowrates_kg_hr = [9235, 23087, 57719, 92350, 161613, 230876, 300138]

    # Idemyldring.
    # Vurdere en egen klasse her som samler inn data? Evt fra notatblokk? Excel ark?
    # La oss si nokken skal bruke programmet, kor skal dei legge inn verdiane?
    # Kanskje lage en 'excel' mal for å legge inn tall, den leser og legger alt inn her.

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
        return np.interp(flowrate, self.flowrates_kg_hr, uncertainty)

    ##################################################################################################################################
    # Field uncertainty
    #################################################################################################################################

    def get_field_condition_std(self, flowrate):
        
        field_cond_data = [1.2,0.55,0.3,0.23,0.18,0.2,0.24] #random numbers, no data behind.
        return self.linear_interpolation(flowrate, field_cond_data)

    def get_field_repeatability_std(self, flowrate):

        field_rep_data = [0.2, 0.55, 0.18, 0.3,  0.24, 0.23, 1.2] #random numbers, no data behind
        return self.linear_interpolation(flowrate, field_rep_data)

    def calculate_field_sum_variance(self, *args):
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
    # Calibration uncertainty
    #################################################################################################################################

    def get_calibration_deviation_std(self, flowrate):
        """
        
        
        
        """

        # deviation = [1.2,0.55,0.3,0.23,0.18,0.2,0.24] # in percentage, (uncorrected)
        deviation = [0.145, 0.145, 0.145, 0.145, 0.145, 0.145, 0.145]
        return self.linear_interpolation(flowrate, deviation)

    def get_calibration_reference_std(self, flowrate):
        # Depends on metering equpiment used at flow laboratory, and will be found in
        # calibration certificate. Can vary with flowrate.

        reference = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]  # In percentage, std
        return self.linear_interpolation(flowrate, reference)

    def get_calibration_repeatability_std(self, flowrate):
        # Kan variere med flow.
        # This term covers repeatability of the Coriolis flow meter
        # to be calibrated and the reference measurement.
        # This varies with flow rate - use linear interpolation between points.

        repeatability = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]  # In percentage
        return self.linear_interpolation(flowrate, repeatability)

    def calculate_calibration_sum_variance(self, flowrate):
        return (
            self.get_calibration_deviation_std(flowrate) ** 2
            + self.get_calibration_repeatability_std(flowrate) ** 2
            + self.get_calibration_reference_std(flowrate) ** 2
        )


    def calculate_relative_uncertainty(self, flowrate):
        if flowrate == 0:
            return 0
        # Sum of variances. In %**2
        sum_of_variance = self.calculate_calibration_sum_variance(
            flowrate
        ) + self.calculate_field_sum_variance(flowrate)
        relative_combined_std_uncertainty = math.sqrt(sum_of_variance)
        return self.convert_std_to_confidence(relative_combined_std_uncertainty)

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


def run(flowrate):
    uncertainty = UncertaintyTools().calculate_relative_uncertainty(flowrate)
    print(uncertainty)


run(9235)
