# Eventuell klasse - kan også legges inn med uncertainty - som vil gjøre korreksjon for 
# trykk og temperatur.

# Dødvolum - dersom valg av måler før varmeveksler.

import math


class correction:
    def __init__(self):
        # Pipe variables
        self.radius = 0.25
        self.height = 15
        self.volume = None
        
        self.R = 8.314 #J/(mol * k)
        self.temperature = -40 #C
        
        # Inital values
        self.pressure_initial = 350 #bar
        self.temperature_initial = None
        
        # Subsequent values
        self.pressure_subsequent = 700 #bar
        self.temperature_subsequent = None



    def calculate_pipe_volume(self, radius, height):
        self.volume = math.pi*radius**2*height


    def calculate_ideal_gas_law_n(self, P, V, R, T):
        n = (P*V) / (R*T)
        return n
    
    def calculate_ideal_gas_law_V(self, delta_n, ):
        V = (delta_n * self.R * self.temperature) / self.pressure_subsequent
        return V

    def correction(self):
    #First calculate initial number of moles
        n_initial = self.calculate_ideal_gas_law_n(self.pressure_initial, self.volume, self.R, self.temperature)

    #Calculate subsequent number of moles
        n_subsequent = self.calculate_ideal_gas_law_n(self.pressure_subsequent, self.volume, self.R, self.temperature)
        delta_n = n_subsequent - n_initial

    # Then calculate the dead volume based of change in number of moles 
        dead_volume = self.calculate_ideal_gas_law_V(delta_n)
        return dead_volume

