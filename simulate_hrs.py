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

    def generate_flowrate_kg_sec(self, vehicle_tank_size_kg=5):
        """ 
        #TODO: Bruk h2filling til å lage bra fyllingsdata + trykk
        Work in progress.
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/second. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        """
        maximum_flowrate_kg_s = 60/1000 # 60 (g/s) / 1000 = kg/s
        max_mass = vehicle_tank_size_kg # grams
        flowrate_increments = (60/1000)/162
        mass_delivered = 0
        flowrate = 0
        flowrates = []
        temps = []
        temp = 20
        temp_increments = 1
        max_temp = -40

        while mass_delivered < max_mass:
            #print(flowrate)
            # Øk flowrate til maksimum er nådd
            if flowrate < maximum_flowrate_kg_s:
                flowrate += flowrate_increments
                flowrate = min(flowrate, maximum_flowrate_kg_s)
            if temp > max_temp:
                temp -= temp_increments
                temp = max(temp, max_temp)

            flowrates.append(flowrate)
            temps.append(temp)
            mass_delivered += flowrate
        #print(f"Mass delivered: {mass_delivered}")
        pressures = np.linspace(0, 700, len(flowrates))
        return flowrates, pressures, temps
