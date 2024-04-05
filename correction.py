"""
Correction module

This module calculates the amount system must correct for to ensure no error
due to dead-volume and vented hydrogen. 

Classes:
    Correction: A class that gives methods for correcting nessecary errors.
"""

import math

class Correction:
    """
    Gives methods for calculating correctional errors.
    """
    def __init__(self):
        # Pipe variables
        self.radius = 0.25
        self.height = 15
        self.volume = 2.94375  # self.calculate_pipe_volume()
        self.gas_constant = 8.314  # J/(mol * k)
        # self.temperature = -40 #C
        # Inital values
        self.pressure_initial = 700  # bar
        self.temperature_initial = 233.15  # Kelvin
        # Subsequent values
        self.pressure_subsequent = 350  # bar
        self.temperature_subsequent = 233.15  # kelvin

    def calculate_pipe_volume(self):
        """
        Calculates the volume of a pipe.
        """
        self.volume = math.pi * self.radius**2 * self.height

    def calculate_ideal_gas_law_n(self, P, V, R, T):
        """
        Utilizes the ideal gas law to calculate the amount of moles n.
        """
        return (P * V) / (R * T)

    def calculate_ideal_gas_law_V(self, delta_n):
        """
        Calculate the volume V
        """
        V = (
            delta_n * self.gas_constant * self.temperature_subsequent
        ) / self.pressure_subsequent
        return V
    
    def calculate_vented_mass(self, volume_vent, current_density):
        """
        Calculates the mass of hydrogen lost due to depressurization of the dispenser hose.
        Parameters:
            - v_vv = volume of piping containing vent gas
            - p_2 = hydrogen density at end of filling
        Returns:
            - density of hydrogen at the end of current fueling
        """
        m_vv = volume_vent * current_density
        return m_vv
    
    def calculate_dead_volume(self, dead_volume, previous_density, current_density):
        """
        Calculates dead volume based off (IMEKO,2022). 
        Parameters:
            - Dead_volume: volume of piping between flow meter and cutoff valve
            - Previous density calculated by hydrogen density equation
            - Current density calculated by hydrogen density equation
        Returns:
            - Dead volume to be substracted from mass delivered total.
        """
        
        dead_volume_mass = dead_volume(current_density - previous_density)
        return dead_volume_mass
    

    def check_correction(self, total_mass_delivered, dead_volume):
        if self.pressure_initial < self.pressure_subsequent:
            print("The customer should recieve less hydrogen than ordered.")
        if self.pressure_subsequent < self.pressure_initial:
            print("The customer should get more hydrogen than ordered.")

        print(f"Total mass delivered (uncorrected): {total_mass_delivered} kg")
        print(
            f"Total mass delivered (corrected): {total_mass_delivered - dead_volume} kg"
        )
