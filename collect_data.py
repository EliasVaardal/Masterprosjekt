"""
This module contains the Collectdata class, which collects data from the user
through the Excel sheet template. This is done in steps, as there are multiple
tables containing different types of data.
"""
import os
import openpyxl
import pandas as pd
from hrs_config import HRSConfiguration


class CollectData:
    """
    This class retrieves data from the Excel file, acting as the communication unit between
    the program and the user. It directly stores data into objects created outside this module.
    """

    def __init__(self, hrs_configs: HRSConfiguration):
        # pylint: disable = W1401
        """
        Creating an instance of the CollectData class requires the hrs_configuration
        and filepath. This is to setup the link between the Excel template and the
        program, and effectively store the data directly to the HRS configuration.

        Parameters:
            - hrs_config: An instance of the HRS configuration class
            - filepath: The path to the Excel template.

        Tips:
            To easily find the correct filepath, find the template in its folder,
            shift+right click and copy path. The filepath will be given by either:
            r"C:\Path\To\Your\Master_project_sheet.xlsx"
            "C:/Path/To/Your/Master_project_sheet.xlsx"
        """
        self.hrs_config = hrs_configs
        self.file_path = self.get_filepath()

        self.config_sheet = "HRS_config"
        self.calibration_sheet = "Calibration_uncertainty"
        self.field_sheet = "Field_uncertainty"
        self.write_sheet = "Write"

        self.single_meter_uncertainties = None
        self.calibration_data = None
        self.field_data = None
        self.config_data = None
        self.volume_data = None
        self.sensor_data = None

        self.read_file()
        self.set_table_1_config()
        self.set_table_2_config()
        self.set_table_3_config()
        self.set_hrs_uncertainty()
        self.read_previous_pressure()
        self.write_previous_pressure()

    def get_filepath(self):
        """
        Returns the 
        """
        program_dir = os.path.dirname(os.path.abspath(__file__))
        dynamic_file_path = os.path.join(program_dir, "excel_template", "configurationtemplate.xlsx")
        return dynamic_file_path

    def write_previous_pressure(self, density=300):
        excel_book = openpyxl.load_workbook(self.file_path)
        sheet = excel_book["Write"]
        sheet['C3'] = density
        excel_book.save(self.file_path)


    def read_previous_pressure(self):
        """
        Reads the previous pressure written by the previous program,
        and stores it in the hrs_config class.
        """
        df = pd.read_excel(
            self.file_path, sheet_name=self.write_sheet, header=1, index_col=0
        )
        self.hrs_config.previous_pressure = df.iloc[0, 1].astype(float)


    def read_file(self):
        """
        Reads an excel file, through the path given defined in __init__.
        The data is then stored in the object parameters for further work
        in subsequent methods.

        Parameters:
            None

        Returns:
            None
        """
        # Collect multiple uncertainties calibration
        df = pd.read_excel(
            self.file_path, sheet_name=self.calibration_sheet, header=1, index_col=0
        )
        #print(df)
        self.calibration_data = df.to_dict(orient="List")
        #print(f"Calib: {self.calibration_data}")

        # Collect multiple uncertaintainties field.
        df = pd.read_excel(
            self.file_path, sheet_name=self.field_sheet, header=1, index_col=0
        ).astype(float)
        #print(df)
        self.field_data = df.to_dict(orient="List")

        # Collect decisions
        df = pd.read_excel(self.file_path, sheet_name=self.config_sheet)
        #print(df)
        table1_specific_cells = df.iloc[[2, 3, 5, 6, 7, 8, 9], 2]  # YES/NO
        #print(table1_specific_cells)
        self.config_data = table1_specific_cells.to_dict()

        # Collect single value calibration and field uncertainties
        table1_uncertainties = df.iloc[[5, 6, 7, 8, 9], 3].astype(float)
        #print(table1_uncertainties)
        self.single_meter_uncertainties = table1_uncertainties.to_dict()

        # Collect table 2 volumes and related uncertainties
        table2_specific_cells = df.iloc[[5, 6, 7], [7, 9]].astype(float)
        self.volume_data = table2_specific_cells.to_dict(orient="index")

        # Collect table 3 sensor uncertainty
        table3_specific_cells = df.iloc[[10, 11], [7]].astype(float)
        self.sensor_data = table3_specific_cells.to_dict(orient="index")

    def convert_decision_to_bool(self, my_dict, index):
        """
        The Excel file contains decisions which are set as YES or NO. This
        acesses a dictionary of YES or NO, and based on its index converts
        YES to boolean: True and No to boolean: False.

        Parameters:
            - my_dict: Dictionary containing either YES or NO.
            - index: the index to check for in the dict.
        """
        if my_dict[index] == "YES":
            return True
        elif my_dict[index] == "NO":
            return False
        else:
            raise ValueError(
                "Decision value not recognized. Make sure it is (YES) or (NO)"
            )

    def set_table_1_config(self):
        """
        Method to be called after read_file(). This method convers the data stored
        in object parameters, directly to the already initialized hrs_configuration class.
        """
        # Table 1 configuration
        self.hrs_config.correct_for_dead_volume_bool = self.convert_decision_to_bool(
            self.config_data, 2
        )
        self.hrs_config.correct_for_depress_bool = self.convert_decision_to_bool(
            self.config_data, 3
        )
        self.hrs_config.multiple_calibration_deviation_bool = (
            self.convert_decision_to_bool(self.config_data, 5)
        )
        self.hrs_config.multiple_calibration_reference_bool = (
            self.convert_decision_to_bool(self.config_data, 6)
        )
        self.hrs_config.multiple_calibration_repeatability_bool = (
            self.convert_decision_to_bool(self.config_data, 7)
        )
        self.hrs_config.multiple_field_repeatability_bool = (
            self.convert_decision_to_bool(self.config_data, 8)
        )
        self.hrs_config.multiple_field_condition_bool = self.convert_decision_to_bool(
            self.config_data, 9
        )

    def set_table_2_config(self):
        self.hrs_config.dead_volume = self.volume_data[5]["Unnamed: 7"]  # H7
        self.hrs_config.dead_volume_uncertainty = self.volume_data[5][
            "Unnamed: 9"
        ]  # J7
        self.hrs_config.depressurization_vent_volume = self.volume_data[6][
            "Unnamed: 7"
        ]  # H8
        self.hrs_config.depressurization_vent_volume_uncertainty = self.volume_data[6][
            "Unnamed: 9"
        ]  # J8


    def set_table_3_config(self):
        # Table 3 uncertainty
        self.hrs_config.temperature_sensor_uncertainty = self.sensor_data[10][
            "Unnamed: 7"
        ]
        self.hrs_config.pressure_sensor_uncertainty = self.sensor_data[11]["Unnamed: 7"]


    def set_hrs_uncertainty(self):
        """
        Based on the decisions made in the Excel template, previously gathered,
        it either sets the uncertainty related to the meter to a single value,
        or as a list of flowrates, which will later be used for linear
        interpolation.

        Parameters:
            - None

        Returns:
            - None
        """
        self.hrs_config.flowrates_kg_min = self.calibration_data["Flowrate [kg/min]"]
        # Calibration deviation correction
        if self.convert_decision_to_bool(self.config_data, 5):
            self.hrs_config.calibration_deviation_std = self.calibration_data[
                "Calibration Deviation u(cal,dev) [%]"
            ]
            #print(self.hrs_config.calibration_deviation_std)
        else:
            self.hrs_config.calibration_deviation_std = self.single_meter_uncertainties[
                5
            ]
        # Calibration reference # # # # # # # #
        if self.convert_decision_to_bool(self.config_data, 6):
            self.hrs_config.calibraiton_reference_std = self.calibration_data[
                "Calibration Reference u(cal,ref) [%]"
            ]
        else:
            self.hrs_config.calibraiton_reference_std = self.single_meter_uncertainties[
                6
            ]
        # Calibration repeatability # # # # # # # #
        if self.convert_decision_to_bool(self.config_data, 7):
            self.hrs_config.calibration_repeatability_std = self.calibration_data[
                "Calibration Repeatability u(cal,rept) [%]"
            ]
        else:
            self.hrs_config.calibration_repeatability_std = (
                self.single_meter_uncertainties[7]
            )

        # Field repeatability# # # # #
        if self.convert_decision_to_bool(self.config_data, 8):
            self.hrs_config.field_repeatability_std = self.field_data[
                "Field Repeatability u(field,rept) [%]"
            ]
        else:
            self.hrs_config.field_repeatability_std = self.single_meter_uncertainties[8]

        # Field condition  # # # # # # # #
        if self.convert_decision_to_bool(self.config_data, 9):
            self.hrs_config.field_condition_std = self.field_data[
                "Field Condition u(field,cond) [%]"
            ]
        else:
            self.hrs_config.field_condition_std = self.single_meter_uncertainties[9]


hrs_config = HRSConfiguration()
data_reader = CollectData(hrs_config)
#print(vars(hrs_config))
# data_reader.read_file()
# self.execlfile = r"C:\Users\Elias\Downloads\Master_project_sheet.xlsx"
