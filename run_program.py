"""
This module contains the main testing code, utilizing all classes in the uncertainty calculation program.
"""

#import numpy as np
#import matplotlib.pyplot as plt

# Presents data.
from collect_data import CollectData
from hrs_config import HRSConfiguration
from uncertainty_tools import UncertaintyTools

#from simulate_hrs import GenerateFlowData
#from correction import Correction

#self.file_path = r"C:\Path\To\Your\Master_project_sheet.xlsx"
#self.file_path = "C:/Path/To/Your/Master_project_sheet.xlsx"
#self.file_path = r"C:\Users\elias\OneDrive\Dokumenter\unc_calc_sheet.xlsx"
class RunProgram:
    """
    This class utilizes all avaliable classes to generate massflow data(Class GenerateFlowData),
    read data input from the Excel file (CollectData), store data as a HRS configuration(HRSConfig),
    calculate uncertainty based on file data(UncertaintyTools), correct the errors (Correction)
    and finally contains methods to present the data.
    """
    def __init__(self):
        self.file_path = r"C:\Users\Elias\Downloads\unc_calc_sheet.xlsx"
        self.hrs_config = HRSConfiguration()
        self.data_reader = CollectData(self.hrs_config, self.file_path)
        self.data_reader.read_file()
        self.data_reader.gather_data_config()

        

        self.uncertaintytools = UncertaintyTools(self.hrs_config)

RunProgram()
