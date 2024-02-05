# Eventuell klasse - kan også legges inn med uncertainty - som vil gjøre korreksjon for 
# trykk og temperatur.

# Dødvolum - dersom valg av måler før varmeveksler.

import math


class correction:
    def __init__(self):
        # Pipe variables
        self.radius = 0.25
        self.height = 15
        self.volume = 2.94375 #self.calculate_pipe_volume()
        
        self.R = 8.314 #J/(mol * k)
        #self.temperature = -40 #C
        
        # Inital values
        self.pressure_initial = 700 #bar
        self.temperature_initial = 233.15 #Kelvin 
        
        # Subsequent values
        self.pressure_subsequent = 350 #bar
        self.temperature_subsequent = 233.15 #kelvin


    def calculate_pipe_volume(self):
        self.volume = math.pi*self.radius**2*self.height


    def calculate_ideal_gas_law_n(self, P, V, R, T):
        n = (P*V) / (R*T)
        return n
    
    def calculate_ideal_gas_law_V(self, delta_n, ):
        V = (delta_n * self.R * self.temperature) / self.pressure_subsequent
        return V

    def calculate_dead_volume(self):
    #First calculate initial number of moles
        n_initial = self.calculate_ideal_gas_law_n(self.pressure_initial, self.volume, self.R, self.temperature)

    #Calculate subsequent number of moles
        n_subsequent = self.calculate_ideal_gas_law_n(self.pressure_subsequent, self.volume, self.R, self.temperature)
        delta_n = n_subsequent - n_initial

    # Then calculate the dead volume based of change in number of moles 
        dead_volume = self.calculate_ideal_gas_law_V(delta_n)
        return dead_volume
    
    def check_correction(self, totalMassDelivered, dead_volume):
        if(self.pressure_initial < self.pressure_subsequent):
            print("The customer should recieve less hydrogen than ordered.")
        if(self.pressure_subsequent < self.pressure_initial):
            print("The customer should get more hydrogen than ordered.")
        
        print(f"Total mass delivered (uncorrected): {totalMassDelivered} kg")
        print(f"Total mass delivered (corrected): {totalMassDelivered - dead_volume} kg")



