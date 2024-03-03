import pandas as pd

class CollectData:
    def __init__(self):
        self.execlfile = "unc_calc_sheet.xlsx"
        self.sheet1 = "Calibration_uncertainty"
        self.sheet2 = "Field_Uncertainty"
        self.sheet3 = "dead_volume_data"
    
    def read_file(self):
        # Read all sheets into a dictionary
        df_dict = pd.read_excel(self.execlfile, sheet_name=self.sheet1, header=1)
        print(df_dict["Flowrate [kg/hr]"])


data_reader = CollectData()
data_reader.read_file()