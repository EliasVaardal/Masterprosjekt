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
        self.pre_fill_pressure = 35000000  #Pa TODO: pascal
        self.pre_fill_temp = 233.15  # Kelvin
        self.post_fill_pressure = None
        self.post_fill_temp = None

    def calculate_vented_mass_error(self, volume_vent, density):
        """
        Calculates the mass of hydrogen lost due to depressurization of the dispenser hose.
        Parameters:
            - v_vv = volume of piping containing vent gas [m3]
            - p_2 = hydrogen density at end of filling [kg/m3]¨

        Returns:
            - Mass vented at end of filling [kg]
        """
        m_vv = volume_vent * density
        return m_vv

    def calculate_dead_volume_mass_error(self, previous_density, current_density, volume):
        """
        Calculates dead volume based off (IMEKO,2022).

        Parameters:
            - Previous density calculated by hydrogen density equation [kg/m3].
            - Current density calculated by hydrogen density equation [kg / m3].

        Returns:
            - Dead volume to be substracted from mass delivered total [kg].
        """
        dead_volume_mass =  volume * (current_density - previous_density)
        return dead_volume_mass

    def calculate_total_correction_error(self, pre_press,pre_temp, post_press, post_temp,):
        """
        Calculates the total correction error from dead volume and depressurized vent.

        Parameters:
            - Initial_pressure : Pressure from previous filling [Pa]
            - Inital_temperature : Temperature from previous filling [Kelvin]
            - Subsequent_pressure : Pressure at the end of current filling [Pa]
            - Subsequent_temperature : Temperature at the end of current filling [Kelvin]
        
        Returns:
            - Total_error: Total error to be corrected [kg]
            - vented_mass: Amount of systematic mass error due to vents [kg]
            - dv_mass_error: Amount of mass error due to dead volume [kg]
        """
        #Collect volumes from configuration
        volume_dv = self.hrs_config.get_dead_volume()
        volume_vv = self.hrs_config.get_depressurization_vent_volume()
        
        # Calculate density based on corresponding pressures and temperatures
        prev_density = self.flow_properties.calculate_hydrogen_density(pre_press, pre_temp)
        curr_density = self.flow_properties.calculate_hydrogen_density(post_press, post_temp)

        # Calculate dead volume mass error
        dv_mass_error = self.calculate_dead_volume_mass_error(prev_density, curr_density, volume_dv)

        #Calculate vented mass error
        vented_mass = self.calculate_vented_mass_error(prev_density, volume_vv)

        #print(f"Dead volume mass {dv_mass_error} Vented mass: {vented_mass}")
        total_error = dv_mass_error + vented_mass
        return total_error, vented_mass, dv_mass_error
