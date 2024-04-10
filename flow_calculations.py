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
        self.molar_mass_m = 2.01568*(10**-3)  # (g/mol)*10^-3   ->   2.016×10−3 kg/mol.
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
            self - q_m: Flow rate
        Returns:
            Calculated energy flowrate value []
        """
        return self.h_sm * self.q_m
    

    def calculate_hydrogen_density(self, pressure, temperature, volume):
        """
        https://en.wikipedia.org/wiki/Ideal_gas_law
        Calculate the hydrogen by utilizing the ideal gas law. This is done by
        utilizing molar mass [kg/mol], and gas constant R [J/(mol*K)], aswell
        as the in-parameters. 

        Parameters:
            - Pressure: Pressure of the gas (Pa)
            - Temperature: Temperature of the gas (Kelvin)
            - Volume: Volume of the gas [m3]

        Returns: 
            Calculated density (kg/m3)
        """
        n = (pressure *volume ) / (self.gas_constant_r*temperature)
        density2 = n*self.molar_mass_m / volume

        #density1 = (pressure * self.molar_mass_m) / (self.gas_constant_r*temperature)
        #print(f"Density gamle: {density2} Density nye {density1}")
        return density2
