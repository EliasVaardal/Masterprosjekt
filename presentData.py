# This class will serve as the final output of the structure. 

# Presents data.
import simulateHRS
import correction
import uncertaintyTools
import numpy as np

class presentData:
    def __init__(self) -> None:
        self.simulation = simulateHRS.simulateHRS()
        self.uncertainty = uncertaintyTools.uncertaintyTools()
        self.correction = correction.correction()

        self.totalMassDelivered = 0

    def main(self):
        # Kaller metoder fra klasse instansene laget i initialize.
        massflow_simulation = self.simulation.generate_simulation_mean()
        
        print("Simulating mass flow for a HRS with a 95% confidence interval")
        for massflow in massflow_simulation:
            self.totalMassDelivered += massflow
            uncertainty = self.uncertainty.calculate_relative_uncertainty(massflow)
            print(f"Flow rate: {massflow} ± {np.around(uncertainty,3)}%  kg/min ")


        #Regner ut korregeringer.
        dead_volume = self.correction.calculate_dead_volume()
        self.correction.check_correction(self.totalMassDelivered, dead_volume)
data_presenter = presentData()
data_presenter.main()
        
