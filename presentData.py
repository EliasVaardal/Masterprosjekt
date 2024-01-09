# This class will serve as the final output of the structure. 

# Presents data.
import simulateHRS
import Uncertainty
import numpy as np

class presentData:
    def __init__(self) -> None:
        self.simulation = simulateHRS.simulateHRS()
        self.uncertainty = Uncertainty.uncertaintyTools()

    def main(self):
        massflow_simulation = self.simulation.generate_simulation_mean()
        print("Simulating mass flow for a HRS with a 95% confidence interval")
        for massflow in massflow_simulation:
            uncertainty = self.uncertainty.calculate_relative_uncertainty(massflow)
            print(f"Flow rate: {massflow} ± {np.around(uncertainty,2)}%  kg/min ")
    
data_presenter = presentData()
data_presenter.main()
        
