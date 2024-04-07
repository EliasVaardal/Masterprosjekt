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
        #HRS Decisions
        self.correct_for_dead_volume_bool = None
        self.correct_for_depress_bool = None
        self.multiple_calibration_deviation_bool = None
        self.multiple_calibration_reference_bool = None
        self.multiple_calibration_repeatability_bool = None
        self.multiple_field_repeatability_bool = None
        self.multiple_field_condition_bool = None

        # Table 2 volume and related uncertainties.
        self.dead_volume_size = None
        self.depressurization_vent_volume = None
        self.dispenser_hose_volume = None
        self.dispenser_hose_volume_uncertainty = None
        self.dead_volume_size_uncertainty = None
        self.depressurization_vent_volume_uncertainty = None

        # Meter Uncertainties
        self.flowrates_kg_min = None # Flowrates for linear interpolation use.
        self.calibraiton_reference_std = None
        self.calibration_repeatability_std = None
        self.calibration_deviation_std = None
        self.field_repeatability_std = None
        self.field_condition_std = None

    def get_dead_volume_size(self):
        return self.dead_volume_size
    
    def get_depressurization_vent_volume(self):
        return self.depressurization_vent_volume
    
    def get_dispenser_hose_volume(self):
        return self.dispenser_hose_volume
    
    def get_correct_for_dead_volume(self):
        return self.get_correct_for_dead_volume
    
    def get_correct_for_depress(self):
        return self.correct_for_depress_bool
    
    def get_calibration_deviation(self):
        return self.calibration_deviation_std
    
    def get_calibration_reference(self):
        return self.calibraiton_reference_std
    
    def get_calibration_repeatability(self):
        return self.calibration_repeatability_std
    
    def get_field_repeatability(self):
        return self.field_condition_std
    
    def get_field_condition(self):
        return self.field_condition_std
