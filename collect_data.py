import pandas as pd


class CollectData:
    def __init__(self):
        """
        Initialize CollectData object.
        """
        self.file_path = r"C:\Path\To\Your\Master_project_sheet.xlsx"
        self.sheet1 = "Calibration uncertainty"
        self.sheet2 = "Field uncertainty"
        self.sheet3 = "dead volume data"

        self.calibration_data = None
        self.field_data = None
        self.pipe_data = None

    def read_file(self):
        # Calibration
        df_dict = pd.read_excel(self.file_path, sheet_name=self.sheet1, header=2)
        self.calibration_data = df_dict.to_dict(orient="List")

        # field
        df_dict = pd.read_excel(self.file_path, sheet_name=self.sheet2, header=2)
        self.field_data = df_dict.to_dict(orient="List")

        # pipe
        # df_dict = pd.read_excel(self.execlfile, sheet_name=self.sheet3, header=2, index_col=0)
        # self.pipe_data = df_dict.to_dict(orient='List')

    def get_calibration_data(self):
        return self.calibration_data

    def get_field_data(self):
        return self.field_data


# data_reader = CollectData()
# data_reader.read_file()
# self.execlfile = r"C:\Users\Elias\Downloads\Master_project_sheet.xlsx"
