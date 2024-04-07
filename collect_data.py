"""
This module contains the Collectdata class, which collects data from the user
through the Excel sheet template.
"""

import pandas as pd

from hrs_config import HRSConfiguration

class CollectData:
    """
    This class retrieves data from the Excel file, acting as thecommunication unit between
    the program and the user. It directly stores data into objects created outside this module.
    """
    def __init__(self, hrs_configs : HRSConfiguration, filepath):
        """
        The CollectData stores all user input in the class HRSConfiguration.
        Thus, this class is used as a paramter for the CollectData oject.
        """
        # Classes which data will be added to.
        self.hrs_config = hrs_configs
        self.file_path = filepath

        self.config_sheet = "hrs_config"
        self.calibration_sheet = "Calibration_uncertainty"
        self.field_sheet = "Field_uncertainty"
        
        self.single_meter_uncertainties = None
        self.calibration_data = None
        self.field_data = None
        self.config_data= None
        self.volume_data = None


    def read_file(self):
        """
        Reads an excel file, through the path given defined in __init__.
        Parameters:
            None
        Returns:
            None
        """
        # Collect multiple uncertainties calibration
        df = pd.read_excel(self.file_path, sheet_name=self.calibration_sheet, header=1, index_col=0)
        self.calibration_data = df.to_dict(orient="List")

        # Collect multiple uncertaintainties field.
        df = pd.read_excel(self.file_path, sheet_name=self.field_sheet, header=1, index_col=0)
        self.field_data = df.to_dict(orient="List")

        # Collect decisions
        df = pd.read_excel(self.file_path, sheet_name=self.config_sheet)
        table1_specific_cells = df.iloc[[2, 3, 5, 6, 7, 8, 9],2] #YES/NO
        self.config_data = table1_specific_cells.to_dict()

        # Collect single valuescalibration and field uncertainties
        table1_uncertainties = df.iloc[[5, 6, 7, 8, 9],3]
        self.single_meter_uncertainties = table1_uncertainties.to_dict()

        # Collect table 2 volumes and related uncertainties
        table2_specific_cells = df.iloc[[5, 6, 7], [7, 9]]
        self.volume_data = table2_specific_cells.to_dict(orient='index')
        
        #print(self.single_meter_uncertainties)

    def gather_data_config(self):
        # Table 1 configuration
        self.hrs_config.correct_for_dead_volume_bool = self.convert_decision_to_bool(self.config_data,2)
        self.hrs_config.correct_for_depress_bool = self.convert_decision_to_bool(self.config_data,3)
        self.hrs_config.multiple_calibration_deviation_bool = self.convert_decision_to_bool(self.config_data, 5)
        self.hrs_config.multiple_calibration_reference_bool = self.convert_decision_to_bool(self.config_data, 6)
        self.hrs_config.multiple_calibration_repeatability_bool = self.convert_decision_to_bool(self.config_data, 7)
        self.hrs_config.multiple_field_repeatability_bool = self.convert_decision_to_bool(self.config_data, 8)
        self.hrs_config.multiple_field_condition_bool = self.convert_decision_to_bool(self.config_data, 9)

        self.set_hrs_uncertainty()

        # Table 2 configuration
        self.hrs_config.dead_volume_size = self.volume_data[5]['Unnamed: 7'] # H7
        self.hrs_config.dead_volume_size_uncertainty=self.volume_data[5]['Unnamed: 9'] # J7
        self.hrs_config.depressurization_vent_volume = self.volume_data[6]['Unnamed: 7'] # H8
        self.hrs_config.depressurization_vent_volume_uncertainty = self.volume_data[6]['Unnamed: 9'] # J8
        self.hrs_config.dispenser_hose_volume = self.volume_data[7]['Unnamed: 7'] # H9
        self.hrs_config.dispenser_hose_volume_uncertainty = self.volume_data[7]['Unnamed: 9'] # J9
        #print(self.hrs_config.field_condition_std)

    def set_hrs_uncertainty(self):
        self.hrs_config.flowrates_kg_min = self.calibration_data["Flowrate [kg/hr]"]

        # Calibration deviation correction
        if self.convert_decision_to_bool(self.config_data, 5):
            self.hrs_config.calibration_deviation_std = self.calibration_data["Calibration Deviation u(cal,dev)"]
        else:
            self.hrs_config.calibration_deviation_std = self.single_meter_uncertainties[5]
        # Calibration reference # # # # # # # #
        if self.convert_decision_to_bool(self.config_data, 6):
            self.hrs_config.calibraiton_reference_std = self.calibration_data["Calibration Reference u(cal,ref)"]
        else:
            self.hrs_config.calibraiton_reference_std= self.single_meter_uncertainties[6]
        # Calibration repeatability # # # # # # # #
        if self.convert_decision_to_bool(self.config_data, 7):
            self.hrs_config.calibration_repeatability_std = self.calibration_data["Calibration Repeatability u(cal,rept)"]
        else:
            self.hrs_config.calibraiton_reference_std= self.single_meter_uncertainties[7]
        
        # Field repeatability# # # # #
        if self.convert_decision_to_bool(self.config_data, 8):
            self.hrs_config.field_repeatability_std = self.field_data["Field Repeatability u(field,rept)"]
        else:
            self.hrs_config.field_repeatability_std= self.single_meter_uncertainties[8]
        
        # Field condition  # # # # # # # #
        if self.convert_decision_to_bool(self.config_data, 9):
            self.hrs_config.field_condition_std = self.field_data["Field Condition u(field,cond)"]
        else:
            self.hrs_config.field_condition_std= self.single_meter_uncertainties[9]

    def convert_decision_to_bool(self, my_dict, index):
        if my_dict[index] == "YES":
            return True
        elif my_dict[index] == "NO":
            return False
        else:
            raise ValueError("Decision value not recognized. Ma ke sure it is (YES) or (NO)")



# data_reader = CollectData()
# data_reader.read_file()
# self.execlfile = r"C:\Users\Elias\Downloads\Master_project_sheet.xlsx"
