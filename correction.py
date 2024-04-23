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

        self.pre_fill_pressure = 35000000  #C TODO: pascal
        #self.pressure_initial = 700  # bar
        self.pre_fill_temp = 233.15  # Kelvin
        # Subsequent values
        self.post_fill_pressure = 70000000  # pascal
        #self.pressure_subsequent = 350  # bar
        self.post_fill_temp = 273.15  # kelvin

    def calculate_vented_mass_error(self, volume_vent, density):
        """
        Calculates the mass of hydrogen lost due to depressurization of the dispenser hose.
        Parameters:
            - v_vv = volume of piping containing vent gas [m3]
            - p_2 = hydrogen density at end of filling [kg/m3]
        Returns:
            - density of hydrogen at the end of current fueling [kg]
        """
        m_vv = volume_vent * density
        return m_vv

    def calculate_dead_volume_mass_error(self, previous_density, current_density):
        """
        Calculates dead volume based off (IMEKO,2022).

        Parameters:
            - Previous density calculated by hydrogen density equation [kg/m3].
            - Current density calculated by hydrogen density equation [kg / m3].

        Returns:
            - Dead volume to be substracted from mass delivered total [kg].
        """
        dead_volume_mass = self.hrs_config.get_dead_volume() * (
            current_density - previous_density
        )
        return dead_volume_mass

    def check_correction(self, pre_fill_pressure, post_fill_pressure):
        """
        A testing method to test if the actual correction is done correctly,
        only looking at previous and current pressure.

        Will probably be removed.
        """
        if pre_fill_pressure < post_fill_pressure:
            print("The customer should recieve less hydrogen than ordered.")
        if post_fill_pressure < pre_fill_pressure:
            print("The customer should get more hydrogen than ordered.")

    def calculate_total_correction_error(self, pre_press,pre_temp, post_press, post_temp,):
        """ #TODO: Sjekk imeko, er det samme sted tettheten skal bli regnet på.
        Calculates the total correction error from dead volume and depressurized vent.

        Parameters:
            - Initial_pressure : Pressure from previous filling [Pa]
            - Inital_temperature : Temperature from previous filling [Kelvin] #TODO??
            - Subsequent_pressure : Pressure at the end of current filling [Pa]
            - Subsequent_temperature : Temperature at the end of current filling [Kelvin] #TODO??
        """
        dead_volume = self.hrs_config.get_dead_volume()
        depress_vent_volume = self.hrs_config.get_depressurization_vent_volume()
        pre_density_dead_volume = self.flow_properties.calculate_hydrogen_density(
            pre_press, pre_temp, dead_volume
            )
        post_density_dead_volume = self.flow_properties.calculate_hydrogen_density(
                post_press, post_temp, dead_volume
            )
        dead_volume_mass_error = self.calculate_dead_volume_mass_error(
            pre_density_dead_volume, post_density_dead_volume
        )
        density_vent = self.flow_properties.calculate_hydrogen_density(
            post_press,
            post_temp,
            depress_vent_volume,
        )
        vented_mass = self.calculate_vented_mass_error(depress_vent_volume, density_vent)
        print(f"Dead volume mass {dead_volume_mass_error} Vented mass: {vented_mass}")
        total_error = dead_volume_mass_error + vented_mass
        return total_error
