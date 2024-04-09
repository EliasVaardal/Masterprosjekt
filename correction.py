"""
Correction module

This module calculates the amount system must correct for to ensure no error
due to dead-volume and vented hydrogen.

Classes:
    Correction: A class that gives methods for correcting nessecary errors.
"""

from hrs_config import HRSConfiguration
from flow_calculations import FlowProperties


class Correction:
    """
    Gives methods for calculating correctional errors.
    """

    def __init__(self, hrs_config: HRSConfiguration):
        self.hrs_config = hrs_config
        self.flow_properties = FlowProperties()

        # Pipe variables

        self.pressure_initial = 700  # bar
        self.temperature_initial = 233.15  # Kelvin
        # Subsequent values
        self.pressure_subsequent = 350  # bar
        self.temperature_subsequent = 233.15  # kelvin

    def calculate_vented_mass(self, volume_vent, density):
        """
        Calculates the mass of hydrogen lost due to depressurization of the dispenser hose.
        Parameters:
            - v_vv = volume of piping containing vent gas
            - p_2 = hydrogen density at end of filling
        Returns:
            - density of hydrogen at the end of current fueling
        """
        m_vv = volume_vent * density
        return m_vv

    def calculate_change_in_dead_volume_mass(self, previous_density, current_density):
        """
        Calculates dead volume based off (IMEKO,2022).

        Parameters:
            - Previous density calculated by hydrogen density equation
            - Current density calculated by hydrogen density equation

        Returns:
            - Dead volume to be substracted from mass delivered total.
        """
        dead_volume_mass = self.hrs_config.dead_volume*(current_density - previous_density)
        return dead_volume_mass

    def check_correction(self, total_mass_delivered, dead_volume):
        """
        A testing method to test if the actual correction is done correctly,
        only looking at previous and current pressure. 

        Will probably be removed.
        """
        if self.pressure_initial < self.pressure_subsequent:
            print("The customer should recieve less hydrogen than ordered.")
        if self.pressure_subsequent < self.pressure_initial:
            print("The customer should get more hydrogen than ordered.")
        print(f"Total mass delivered (uncorrected): {total_mass_delivered} kg")
        print(
            f"Total mass delivered (corrected): {total_mass_delivered - dead_volume} kg"
        )

    def calculate_total_correction_error(self, pressure_initial, temperature_initial, pressure_subsequent, temperature_subsequent):
        """
        Calculates the total correction error from dead volume and depressurized vent. 

        Parameters:
            - Initial_pressure : Pressure from previous filling [bar]
            - Inital_temperature : Temperature from previous filling [Kelvin] #TODO??
            - Subsequent_pressure : Pressure at the end of current filling [bar]
            - Subsequent_temperature : Temperature at the end of current filling [Kelvin] #TODO??      
        """
        initial_density_dead_volume = self.flow_properties.calculate_hydrogen_density(pressure_initial, temperature_initial, self.hrs_config.dead_volume) # Return kg/m3 
        subsequent_density_dead_volume = self.flow_properties.calculate_hydrogen_density(pressure_subsequent, temperature_subsequent, self.hrs_config.dead_volume) # Returns kg/m3
        dead_volume = self.calculate_change_in_dead_volume_mass(subsequent_density_dead_volume, initial_density_dead_volume)*1000 # Returns kg, convers to grams #TODO

        density_vent = self.flow_properties.calculate_hydrogen_density(pressure_subsequent, temperature_subsequent, self.hrs_config.depressurization_vent_volume) #Returns kg/m3
        vented_mass = self.calculate_vented_mass(self.hrs_config.depressurization_vent_volume, density_vent)*1000 #Returns kg, convert to grams.

        total_error = dead_volume + vented_mass
        return total_error