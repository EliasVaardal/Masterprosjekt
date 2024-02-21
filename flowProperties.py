import math
#z0 = Gass kompressibilitet ved standard trykk og temp
#R = Universal gass konstant
#t0 = Absolutt standard temperatur
#m = molar masse, neglisjerbar usikkerhet
#p0 = Absolutt standard trykk
#qm = masseflow

#H_s,m = Superior calorific value per mass,  neglisjerbar usikkerhet

# Z_0 / m , compressibility factor



class flowProperties:
    def __init__(self):
        self.Z0 = None #
        self.R =8.31451 #(J/mole K)
        self.T0 = 288.15 #K, = 15°C
        self.m = None #(g/mol)
        self.P0 = 1 #atm, = 101325Pa
        self.q_m = None #Mass flow rate

        self.h_sm = None




    def calculate_std_vol_flowrate(self):
        Q_v0=((self.Z0*self.R*self.T0)/(self.m*self.P0))*(self.q_m)
        return Q_v0


    def calculate_energy_flowrate(self):
        q_e = self.h_sm*self.q_m
        return q_e



