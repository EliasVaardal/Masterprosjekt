"""
This module will create a configuration for the Hydrogen refueling station, allowing for a
versatile use of the program. The class hrs_config will take in decision by the operator
through the Excel sheet.
"""

from collect_data import CollectData

class HRSConfiguration:
    """
    This class will store data about the hydrogen refueling station (HRS) configuration, in
    addition to multiple "get" functions to allow for data retrieval. 
    """
    def __init__(self, class_collect_data : CollectData):
        """
        The class will store variables from the Excel sheet. The initial
        values are dummy values :).
        """
        self.data_reader = class_collect_data

        self.dead_volume_size = None
        self.depressurization_vent_volume = None
        self.dispenser_hose_volume = None

        self.correct_for_dead_volume = True
        self.correct_for_depress = True

        self.multiple_calibration_correction = False
        self.multiple_calibration_reference = False
        self.multiple_calibration_repeatability = False
        self.multiple_field_repeatability = False
        self.multiple_field_condition = False

    def set_config(self):
        self.data_reader.

    def get_dead_volume_size(self):
        return self.dead_volume_size
    
    def get_depressurization_vent_volume(self):
        return self.depressurization_vent_volume
    
    def get_dispenser_hose_volume(self):
        return self.dispenser_hose_volume
    
    def get_correct_for_dead_volume(self):
        return self.get_correct_for_dead_volume
    
    def get_correct_for_depress(self):
        return self.correct_for_depress
    
    def get_multiple_calibration_correction(self):
        return self.multiple_calibration_correction
    
    def get_multiple_calibration_reference(self):
        return self.multiple_calibration_reference
    
    def get_multiple_calibration_repeatability(self):
        return self.multiple_calibration_repeatability
    
    def get_multiple_field_repeatability(self):
        return self.multiple_field_repeatability
    
    def get_multiple_field_condition(self):
        return self.multiple_field_condition
