# Denne koden har som mål å generere flowrates som kan ligne på dei under en fylling.
# Har to hoved metoder som lager tall:
# En som lager for minutter, men det er litt rart
# En anna som lager i sekunder, heilt fram til massen når 6kg.



# Bruker en normalfordeling med numpy
# import numpy as np
import time
# Spørsmål - dersom denne implementasjonen blir brukt til å danne testcase

class GenerateFlowData:
    def __init__(self) -> None:
        self.temperature = -40  # Degrees celsius
        self.pressure = 700  # Nominal working pressure
        self.max_flow_rate = 216  # SAE J2601 definerer maks som 3.6kg/min. 3.6*60 = 216
        self.max_flow_rate_g_s = 60 #SAE J2601 60 g /s
        self.massflows = []

    def generate_simulation_mean_minutes(self):
        # Denne klassen kan generere 'mean' som sendes inn i generate_mass_flow n antall ganger.
        # Den har tre nivå: øking av masseflow rate, stabil ved topp, og senking av rate.
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


