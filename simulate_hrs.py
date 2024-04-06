"""
This module will generate flowdata similar to those seen in a HRS.
"""

import numpy as np
# import time

class GenerateFlowData:
    """
    
    """
    def __init__(self) -> None:
        """
        
        """
        self.max_flow_rate_min_s = 3.6 # SAE J2601 definerer maks som 3.6kg/min. 
        self.max_flow_rate_kg_hr = 216   # 3.6*60 = 216
        self.max_flow_rate_g_s = 60 #SAE J2601 60 g /s
        self.massflows = []

    def generate_simulation_mean_minutes(self):
        """
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/minute. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        """
        for flow_rate in range(0, 37):  # Assuming increments of 0.1 for 0 to 3.6
            # print(f"Flow Rate: {flow_rate / 10} kg/s")
            # time.sleep(0.1)
            self.massflows.append(flow_rate / 10)

        # Keep steady flow rate at 3.6 for a duration (e.g., 10 seconds)
        for _ in range(100):
            # print("Flow Rate: 3.6 kg/s")
            # time.sleep(0.1)
            self.massflows.append(flow_rate / 10)

        # Decrease flow rate from 3.6 back to 0
        for flow_rate in range(36, -1, -1):  # Assuming decrements of 0.1 for 3.6 to 0
            # print(f"Flow Rate: {flow_rate / 10} kg/s")
            # time.sleep(0.1)
            self.massflows.append(flow_rate / 10)
        return self.massflows

    def generate_simulation_mean_seconds(self):
        # TODO: Gjør om til g/s. 
        """
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/second. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        """

        maximum_flowrate_kgmin = 36
        mass_delivered = 0
        maximum_flowrate_sec = maximum_flowrate_kgmin / 60
        for flow_rate in range(maximum_flowrate_kgmin+1):
            massflow_kg_second = flow_rate / 600
            mass_delivered+=massflow_kg_second
            self.massflows.append(massflow_kg_second)
        while(mass_delivered<6):
            self.massflows.append(massflow_kg_second)
            mass_delivered+=massflow_kg_second
        return self.massflows


