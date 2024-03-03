# z0 = Gass kompressibilitet ved standard trykk og temp
# R = Universal gass konstant
# t0 = Absolutt standard temperatur
# m = molar masse, neglisjerbar usikkerhet
# p0 = Absolutt standard trykk
# qm = masseflow
# H_s,m = Superior calorific value per mass,  neglisjerbar usikkerhet
# Z_0 / m , compressibility factor


class FlowProperties:
    def __init__(self):
        self.gas_compressibility_z0 = None  #
        self.gas_constant_r = 8.31451  # (J/mole K)
        self.absolute_standard_temperature_t0 = 288.15  # K, = 15°C
        self.molar_mass_m = None  # (g/mol)
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
        return self.h_sm * self.q_m
