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
    def __init__(self):
        """
        Initialize a new GenerateFlowData instance, allowing for access to simulation
        methods.
        """
        #TODO: Er alle disse nødvendige her.
        self.max_flow_rate_kg_hr = 216   # 3.6*60 = 216
        self.max_flow_rate_kg_min = 3.6 # SAE J2601 definerer maks som 3.6kg/min.
        self.max_flow_rate_g_s = 60 #SAE J2601 60 g /s


    def generate_flowrate_grams_seconds(self, vehicle_tank_size_kg=5):
        """
        This method generates flow rates similar to those seen in a HRS, in the
        form of g/second. It has 3 stages, increase, mass_flowrate_top, and 
        decline. The method adds up mass_delivered, and when close to full tank,
        indicated with the input parameter, it delcines swiftly.
        
        Parameters:
            - vehicle_tank_size_kg : Maximum storage capacity in kilograms,
                                    defaults to 5 kilograms.
        
        Returns:
            - An array containing flowrates [int]
        """
        maximum_flowrate_g_s = 60 # g / s, 3.6*1000/60
        maximum_mass = vehicle_tank_size_kg*1000# grams
        flowrate_increments = 2
        mass_delivered = 0
        flowrate = 0
        flowrates = []

        while mass_delivered < maximum_mass:
            # Øk flowrate til maksimum er nådd eller begynn i nedgangsfasen
            if flowrate < maximum_flowrate_g_s:
                flowrate += flowrate_increments
                flowrate = min(flowrate, maximum_flowrate_g_s)

            flowrates.append(flowrate)
            mass_delivered += flowrate

            # Justincase loopbreakr.
            #if flowrate == 0:
            #    break

        #for second, rate in enumerate(flowrates, 1):  # second starter fra 1
        #    print(f"Sekund {second}: Vektningsrate {rate} g/s")

        #print(f"Total masse dispensert: {mass_delivered} g")
        return flowrates

    def generate_flowrate_kg_min(self, vehicle_tank_size_kg=6):
        """
        Work in progress.
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/second. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        """
        maximum_flowrate_kg_min = 3.6 # g / s, 3.6*1000/60
        max_mass = vehicle_tank_size_kg # grams
        flowrate_increments = 0.1
        flowrate_decrements = 0.6  # Reduksjon av flowrate per sekund under nedgang
        mass_delivered = 0
        flowrate = 0
        decline = False
        flowrates = []

        while mass_delivered < max_mass:
            # Øk flowrate til maksimum er nådd
            if not decline and flowrate < maximum_flowrate_kg_min:
                flowrate += flowrate_increments
                flowrate = min(flowrate, maximum_flowrate_kg_min)

            # Sjekker etter start til nedgangsfase
            if not decline and max_mass - mass_delivered - flowrate <= maximum_flowrate_kg_min*2:
                decline = True

            # Om nedgangsfase, reduserer flowrate, og unngå negativ flowrate.
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
    flowrates = simulator.generate_flowrate_grams_seconds()
    for second, rate in enumerate(flowrates, 1):  # second starter fra 1
        print(f"Sekund {second}: Vektningsrate {rate} g/s")

#test_simulation()
