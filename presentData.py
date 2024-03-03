# This class will serve as the final output of the structure. 

import numpy as np

# Presents data.
import SimulateHRS
import correction
import UncertaintyTools


class PresentData:
    def __init__(self) -> None:
        self.simulation = SimulateHRS.SimulateHRS()
        self.uncertainty = UncertaintyTools.uncertaintyTools()
        self.correction = correction.Correction()

        self.total_mass_delivered = 0

    def main(self):
        # Kaller metoder fra klasse instansene laget i initialize.
        massflow_simulation = self.simulation.generate_simulation_mean()
        print("Simulating mass flow for a HRS with a 95% confidence interval")
        for massflow in massflow_simulation:
            self.total_mass_delivered += massflow
            uncertainty = self.uncertainty.calculate_relative_uncertainty(massflow)
            print(f"Flow rate: {massflow} ± {np.around(uncertainty,3)}%  kg/min ")

        #Regner ut korregeringer.
        dead_volume = self.correction.calculate_dead_volume()
        self.correction.check_correction(self.total_mass_delivered, dead_volume)

data_presenter = PresentData()
data_presenter.main()
