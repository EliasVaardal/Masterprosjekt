"""
This module will create a configuration for the Hydrogen refueling station, allowing for a
versatile use of the program. The class hrs_config will take in decision by the operator
through the Excel sheet.
"""


class HRSConfiguration:
    """
    This class will store data about the hydrogen refueling station (HRS) configuration, in
    addition to multiple "get" functions to allow for data retrieval.
    """

    def __init__(self):
        """
        The class will store variables from the Excel sheet. The initial
        values are dummy values :).
        """
        # HRS Decisions
        self.correct_for_dead_volume_bool = None
        self.correct_for_depress_bool = None
        self.multiple_calibration_deviation_bool = None
        self.multiple_calibration_reference_bool = None
        self.multiple_calibration_repeatability_bool = None
        self.multiple_field_repeatability_bool = None
        self.multiple_field_condition_bool = None
        self.include_temp_bool = None
        self.include_pres_bool = None
        self.include_annual_dev_bool = None

        # Table 2 volume and related uncertainties.
        self.dead_volume = None
        self.depressurization_vent_volume = None
        self.dead_volume_uncertainty = None
        self.depressurization_vent_volume_uncertainty = None

        # Meter Uncertainties
        self.flowrates_kg_min = None  # Flowrates for linear interpolation use.
        self.calibraiton_reference_std = None
        self.calibration_repeatability_std = None
        self.calibration_deviation_std = None
        self.field_repeatability_std = None
        self.field_condition_std = None

        self.pressure_contribution = None
        self.temperature_contribution = None
        self.annual_deviation = None
        self.years_since_calibration = None

        # Sensor uncertainties
        self.pressure_sensor_uncertainty = None
        self.temperature_sensor_uncertainty = None

        #Caclculation check
        self.previous_temperature = None

    def convert_relative_to_absolute(self, uncertainty, reference):
        """
        Converts relative uncertainty to absolte uncertainty.

        Parameters: 
            - Relative uncertainty
            - Refere
        """
        absolute_uncertainty = (uncertainty / 100) * reference
        return absolute_uncertainty

    def get_dead_volume(self):
        """The Excel template requires dm3 input, so the code converts dm3 to m3, and
        return the size of the dead volume [m3]."""
        if self.correct_for_dead_volume_bool:
            return self.dead_volume
        else:
            return 0

    def get_dead_volume_uncertainty(self):
        """Return the uncertainty of the dead volume."""
        return self.convert_relative_to_absolute(
            self.dead_volume_uncertainty, self.dead_volume
        )

    def get_depressurization_vent_volume(self):
        """Return the volume of the depressurization vent."""
        if self.correct_for_depress_bool:
            return self.depressurization_vent_volume
        else:
            return 0

    def get_depressurization_vent_volume_unc(self):
        """Return the uncertainty of the volume of the depressurization vent."""
        uncertainty = self.depressurization_vent_volume_uncertainty
        reference = self.depressurization_vent_volume
        return self.convert_relative_to_absolute(uncertainty, reference)

    def get_correct_for_dead_volume(self):
        """Return the correction status for the dead volume."""
        return self.get_correct_for_dead_volume

    def get_correct_for_depress(self):
        """Return whether there is a correction for depressurization."""
        return self.correct_for_depress_bool

    def get_calibration_deviation(self):
        """Return the standard deviation for calibration."""
        return self.calibration_deviation_std

    def get_calibration_reference(self):
        """Return the standard deviation of the calibration reference."""
        return self.calibraiton_reference_std

    def get_calibration_repeatability(self):
        """Return the standard deviation for calibration repeatability."""
        return self.calibration_repeatability_std

    def get_field_repeatability(self):
        """Return the standard deviation for field condition repeatability."""
        return self.field_repeatability_std

    def get_field_condition(self):
        """Return the standard deviation for field conditions."""
        return self.field_condition_std

    def get_pressure_uncertainty(self, pressure):
        """Returns the absolute standard deviation for the pressure sensors uncertainty"""
        return self.convert_relative_to_absolute(
            self.pressure_sensor_uncertainty, pressure
        )

    def get_temperature_uncertainty(self, temperature):
        """Return the absolute standard deviation for the temperature uncertainty"""
        return self.convert_relative_to_absolute(
            self.pressure_sensor_uncertainty, temperature
        )
