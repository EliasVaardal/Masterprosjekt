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

    def generate_flowrate_grams_seconds(self, vehicle_tank_size_kg=5):
        # TODO: Gjør om til g/s. 
        """
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/second. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        """
        maximum_flowrate_g_s = 60 # g / s, 3.6*1000/60
        maximum_mass = 6000 # grams
        flowrate_increments = 2
        flowrate_decrements = 10  # Reduksjon av flowrate per sekund under nedgang
        mass_delivered = 0
        flowrate = 0
        decline = False
        flowrates = []

        while mass_delivered < maximum_mass:
            # Øk flowrate til maksimum er nådd eller begynn i nedgangsfasen
            if not decline and flowrate < maximum_flowrate_g_s:
                flowrate += flowrate_increments
                flowrate = min(flowrate, maximum_flowrate_g_s)

            # Sjekker etter start til nedgangsfase
            if not decline and maximum_mass - mass_delivered - flowrate <= maximum_flowrate_g_s*2:
                decline = True

            # Om nedgangsfase, reduserer flowrate, også ingen negativ flowrate.
            if decline:
                flowrate = max(flowrate - flowrate_decrements, 0)

            flowrates.append(flowrate)
            mass_delivered += flowrate

            # Justincase loopbreakr.
            if flowrate == 0:
                break

        #for second, rate in enumerate(flowrates, 1):  # second starter fra 1
        #    print(f"Sekund {second}: Vektningsrate {rate} g/s")

        #print(f"Total masse dispensert: {mass_delivered} g")
        return flowrates
