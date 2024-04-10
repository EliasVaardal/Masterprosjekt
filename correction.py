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

        self.pre_fill_pressure = 35000000  # TODO: pascal
        #self.pressure_initial = 700  # bar
        self.pre_fill_temp = 233.15  # Kelvin
        # Subsequent values
        self.post_fill_pressure = 70000000  # pascal
        #self.pressure_subsequent = 350  # bar
        self.post_fill_temp = 273.15  # kelvin

    def calculate_vented_mass(self, volume_vent, density):
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

    def calculate_change_in_dead_volume_mass(self, previous_density, current_density):
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

    def calculate_total_correction_error(
        self,
        pressure_initial,
        temperature_initial,
        pressure_subsequent,
        temperature_subsequent,
    ):
        """
        Calculates the total correction error from dead volume and depressurized vent.

        Parameters:
            - Initial_pressure : Pressure from previous filling [Pa]
            - Inital_temperature : Temperature from previous filling [Kelvin] #TODO??
            - Subsequent_pressure : Pressure at the end of current filling [Pa]
            - Subsequent_temperature : Temperature at the end of current filling [Kelvin] #TODO??
        """
        dead_volume = self.hrs_config.get_dead_volume()
        depressurization_vent_volume = self.hrs_config.get_depressurization_vent_volume()
        initial_density_dead_volume = self.flow_properties.calculate_hydrogen_density(
            pressure_initial, temperature_initial, dead_volume
        )
        subsequent_density_dead_volume = (
            self.flow_properties.calculate_hydrogen_density(
                pressure_subsequent, temperature_subsequent, dead_volume
            )
        )

        dead_volume_mass = self.calculate_change_in_dead_volume_mass(
            initial_density_dead_volume, subsequent_density_dead_volume
        )
        density_vent = self.flow_properties.calculate_hydrogen_density(
            pressure_subsequent,
            temperature_subsequent,
           depressurization_vent_volume,
        )  # Returns kg/m3
        vented_mass = self.calculate_vented_mass(
        depressurization_vent_volume, density_vent
        )  # Returns kg, convert to grams.
        print(f"Dead volume mass {dead_volume_mass} Vented mass: {vented_mass}")
        total_error = dead_volume_mass + vented_mass
        return total_error
