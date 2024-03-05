# Denne koden har som mål å generere tall som kan ligne på dei under en fylling.
# Bruker en normalfordeling med numpy

# import numpy as np


# Spørsmål - dersom denne implementasjonen blir brukt til å danne testcase


class SimulateHRS:
    def __init__(self) -> None:
        self.temperature = -40  # Degrees celsius
        self.pressure = 700  # Nominal working pressure
        self.max_flow_rate = 216  # SAE J2601 definerer maks som 3.6kg/min. 3.6*60 = 216
        self.massflows = []

    def generate_simulation_mean(self):
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
