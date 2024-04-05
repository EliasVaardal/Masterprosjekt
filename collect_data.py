import pandas as pd


class CollectData:
    """
    This class retrieves data from the Excel file, acting as the
    communication unit between the program and the user.  
    """
    def __init__(self):
        """
        Initialize CollectData object.
        """
        #self.file_path = r"C:\Path\To\Your\Master_project_sheet.xlsx"
        self.file_path = r"C:\Users\elias\OneDrive\Dokumenter\unc_calc_sheet.xlsx"
        self.sheet1 = "Calibration_uncertainty"
        self.sheet2 = "Field_uncertainty"
        self.sheet3 = "dead_volume_data"

        self.calibration_data = None
        self.field_data = None
        self.pipe_data = None


    def read_file(self):
        """
        Reads an excel file, through the path given defined in __init__.
        Parameters:
            None
        Returns:
            None
        """
        # Calibration
        df_dict = pd.read_excel(self.file_path, sheet_name=self.sheet1, header=1, index_col=0)
        self.calibration_data = df_dict.to_dict(orient="List")
        #for key in self.calibration_data.keys():
        #    print(key)

        # field
        df_dict = pd.read_excel(self.file_path, sheet_name=self.sheet2, header=1, index_col=0)
        self.field_data = df_dict.to_dict(orient="List")

        # pipe
        # df_dict = pd.read_excel(self.execlfile, sheet_name=self.sheet3, header=2, index_col=0)
        # self.pipe_data = df_dict.to_dict(orient='List')

    def get_calibration_data(self):
        """
        Returns calibration data, gathered from an Excel file.
        Paramaters:
            None
        Returns:
            Returns either a [1x1] Pandas DataFrame, or a set of
            values per flow rate in a Pandas DataFrame. 
        """
        return self.calibration_data

    def get_field_data(self):
        """
        Returns field data, gathered from an Excel file.
        Paramaters:
            None
        Returns:
            Returns either a [1x1] Pandas DataFrame, or a set of
            values per flow rate in a Pandas DataFrame. 
        """
        return self.field_data


# data_reader = CollectData()
# data_reader.read_file()
# self.execlfile = r"C:\Users\Elias\Downloads\Master_project_sheet.xlsx"
