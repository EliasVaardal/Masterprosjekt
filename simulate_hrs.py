"""
This module contains the GenerateFlowData class, which will return a list of flowrates which
are similar to those seen in a HRS. The class also offer options for different units, such as
g/s, kg/min, and kg/hr. Finally, the test_simulation() tries the method and prints the flowrates.
Classes:
    GenerateFlowData
Methods:
    test_simulation()
"""

class GenerateFlowData:
    """
    This class contains methods for generating flowrates similar to those seen in
    a HRS.
    """

#TODO: Lag en simulasjon for temp og trykk.

    def generate_flowrate_kg_sec(self, vehicle_tank_size_kg=5):
        """
        Work in progress.
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/second. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        """
        maximum_flowrate_kg_s = 60/1000 # 60 (g/s) / 1000 = kg/s
        max_mass = vehicle_tank_size_kg # grams
        flowrate_increments = (60/1000)/190
        mass_delivered = 0
        flowrate = 0
        flowrates = []

        while mass_delivered < max_mass:
            #print(flowrate)
            # Øk flowrate til maksimum er nådd
            if flowrate < maximum_flowrate_kg_s:
                flowrate += flowrate_increments
                flowrate = min(flowrate, maximum_flowrate_kg_s)

            flowrates.append(flowrate)
            mass_delivered += flowrate
        #print(f"Mass delivered: {mass_delivered}")
        return flowrates

def test_simulation():
    """
    Simulation method. Creates an instance of the class generateflowdata,
    and runs a simulation method, subsequently printing all the flowrates.

    Parameters:
        None
    
    Returns:
        None
    """
    simulator = GenerateFlowData()
    flowrates = simulator.generate_flowrate_kg_sec()
    for second, rate in enumerate(flowrates, 1):  # second starter fra 1
        print(f"Sekund {second}: Vektningsrate {rate} kg/s")

#test_simulation()
