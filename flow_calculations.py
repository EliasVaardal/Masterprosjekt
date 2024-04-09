"""
This module contains the FlowProperties class, which contains methods
for calculating the properties of hydrogen. 

Classes:
    - FlowProperties
Functions:
    - None
"""

# z0 = Gass kompressibilitet ved standard trykk og temp
# R = Universal gass konstant
# t0 = Absolutt standard temperatur
# m = molar masse, neglisjerbar usikkerhet
# p0 = Absolutt standard trykk
# qm = masseflow
# H_s,m = Superior calorific value per mass,  neglisjerbar usikkerhet
# Z_0 / m , compressibility factor


class FlowProperties:
    """
    A class containing methods for calculating the properties of hydrogen, specifically
    standard volumetric flowrate, energy flowrate, and hydrogen density. 
    """
    def __init__(self):
        self.gas_compressibility_z0 = None  #
        self.gas_constant_r = 8.31451  # (J/mole K)
        self.absolute_standard_temperature_t0 = 288.15  # K, = 15°C
        self.molar_mass_m = 2.01568  # (g/mol)
        self.absolute_standard_pressure_p0 = 1  # atm, = 101325Pa
        self.q_m = None  # Mass flow rate
        self.h_sm = None


    def calculate_std_vol_flowrate(self):
        """
        Calculates the standard volumetric flow rate.
        Args:
            self: The instance of the FlowProperties class.

        Returns:
            float: The calculated standard volumetric flow rate.

        Examples:
            # Create an instance of FlowProperties
            flow_props = FlowProperties()

            # Calculate the standard volumetric flow rate
            std_vol_flowrate = flow_props.calculate_std_vol_flowrate()
        """
        return (
            (
                self.gas_compressibility_z0
                * self.gas_constant_r
                * self.absolute_standard_temperature_t0
            )
            / (self.molar_mass_m * self.absolute_standard_pressure_p0)
        ) * (self.q_m)

    def calculate_energy_flowrate(self):
        """
        Calcualtes and returns the energy flow rate. 
        Paramters:
            self - h_sm: superior burn value 
            self - q_m:
        Returns:
            Calculated energy flowrate value []
        """
        return self.h_sm * self.q_m
    
    def calculate_amount_of_moles_n(self, pressure, temperature, volume):
        """
        Calculate amount of moles, based on the ideal gas law.

        Parameters:
            - Pressure
            - Temperature
            - Volume
        
        Returns:
            - Calculated amount of moles n.
        """
        return (pressure *volume ) / (self.gas_constant_r*temperature)


    def calculate_hydrogen_density(self, pressure, temperature, volume):
        """
        Calculate the hydrogen by utilizing the ideal gas law. This is done by
        first calculating number of moles, then mass by number of moles times 

        Parameters:
            - Pressure: Pressure of the gas ()
            - Temperature: Temperature of the gas (Kelvin)
            - Volume: Volume of the gas

        Returns: 
            Calculated density (kg/m3)
        """
        number_of_moles = self.calculate_amount_of_moles_n(pressure, temperature, volume)
        density = number_of_moles*self.molar_mass_m / volume
        return density
