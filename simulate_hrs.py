"""
This module contains the GenerateFlowData class, which will return a list of flowrates which
are similar to those seen in a HRS. The class also offer options for different units, such as
g/s, kg/min, and kg/hr. Finally, the test_simulation() tries the method and prints the flowrates.
Classes:
    GenerateFlowData
Methods:
    test_simulation()
"""
import numpy as np

class GenerateFlowData:
    """
    This class contains methods for generating flowrates similar to those seen in
    a HRS.
    """
    def __init__(self):
        self.max_flowrate_kg_s = 60/1000 # 60 (g/s) / 1000 = kg/s
        self.flowrate_increments = (60/1000)/100
        self.start_temperature = 20
        self.negative_temp_limit = -40
        self.temp_increments = 1


    def generate_filling_protocol_kg_sec(self, vehicle_tank_size_kg):
        """ 
        Work in progress.
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/second. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        """
        mass_delivered = 0
        flowrate = 0
        flowrates = []
        temp = self.start_temperature
        temps = []

        while mass_delivered < vehicle_tank_size_kg:
            #print(flowrate)
            # Øk flowrate til maksimum er nådd
            if flowrate < self.max_flowrate_kg_s:
                flowrate += self.flowrate_increments
                flowrate = min(flowrate, self.max_flowrate_kg_s)
            if temp > self.negative_temp_limit:
                temp -= self.temp_increments
                temp = max(temp, self.negative_temp_limit)
            flowrates.append(flowrate)
            temps.append(temp)
            mass_delivered += flowrate
        pressures = np.linspace(350, 550, len(flowrates))
        return flowrates, pressures, temps
