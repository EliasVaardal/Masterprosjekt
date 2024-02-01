import numpy as np
import math
#TODO: Få kontroll på enheter

#TODO: Få kontroll på usikkerhetsintervall. Kva er u_std, ka er u_95%   

class uncertaintyTools:
    def __init__(self):
        self.k = 2
        self.std_uncertainty_calib_reference = 0.1
        self.std_uncertainty_calib_repeatability = 0.05
        self.std_uncertainty_calib_deviation = 0.145
        self.std_uncertainty_field_repeatability = 0
        self.std_uncertainty_field_conditions = 0
        self.std_uncertainty_zo_m_factor = 0.0261

        self.flowrates_kg_hr = [9235, 23087, 57719, 92350, 161613, 230876, 300138]
        self.flowrates_kg_min = [rate / 60 for rate in self.flowrates_kg_hr]

    ##################################################################################################################################
                        #Uncertainty tools
    #################################################################################################################################

    def convert_std_to_confidence(self, std_uncertainty):
        return self.k*std_uncertainty
    
    def linear_interpolation(self, flowrate, uncertainty):
        return np.interp(flowrate, self.flowrates_kg_min, uncertainty)

    ##################################################################################################################################
                        #Field uncertainty
    #################################################################################################################################

    def get_field_condition_std(self, flowrate):
        # Kan variere med flow.
        # Denne verdien avhenger av installasjon og datablad til flowmeter. Den kan ha forskjellige verdier for relativ usikkerhet
        # ved forskjellige massestrømmer. 

        field_cond = self.std_uncertainty_field_conditions
        return field_cond

    def get_field_repeatability_std(self, flowrate):
        # Kan variere med flow. 
        # Denne blir funnet i datablad, eller egen erfaring. Den sier nokke om kor bra flowmeteret klarer å gjenprodusere like målinger når 
        # den er utsatt for varierande forhold under felt kondisjon.

        field_repeatability = self.std_uncertainty_field_repeatability
        return field_repeatability

    def get_field_uncertainty_std(self, massflow):
        # Felt usikkerhet består av to kontribusjoner:
        # Repeterbarhet til flowmeter under felt kondisjoner
        # Usikkerhet til endring av forhold fra flow kalibrasjon    til felt operasjon

        u_field = (self.get_field_condition_std(massflow) ** 2 +
                    self.get_field_repeatability_confidence(massflow) ** 2) ** 0.5
        return u_field  # Convert to relative uncertainty

    ##################################################################################################################################
                        #Calibration uncertainty
    #################################################################################################################################

    def get_calibration_deviation_std(self, massflow):
        #
        # Calculated from deviation between coriolis mass flow rate and mass flow rate measured by reference ,eter. 
        # See appendix A in NFOGM handbook for calculation.
        
        deviation = [1.2,0.55,0.3,0.23,0.18,0.2,0.24]
        linearized_deviation= self.linear_interpolation(massflow,deviation)
        return linearized_deviation

    def get_calibration_reference_std(self, massflow):
        # Kan  variere med flow.
        # Depends on metering equpiment used at flow laboratory, and will be found in calibration certificate. 
        # Can vary with flowrate.

        reference = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
        linearized_reference= self.linear_interpolation(massflow, reference)
        return linearized_reference

    def get_calibration_repeatability(self, massflow):
        # Kan variere med flow.
        # This term covers repeatability of the Coriolis flow meter to be calibrated and the reference measurement.
        # This varies with flow rate - use linear interpolation between points.
        
        repeatability_95 = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
        linearized_repeatability= self.linear_interpolation(massflow, repeatability_95)
        return linearized_repeatability

    def get_calibration_uncertainty(self, massflow):
        # Calibration uncertainty for a calibrated coriolis mass flowmeter consists of 3 contributions:
        # 1. Uncertainty of correction factor estimate
        # 2. Uncertainty of reference measurement at flow laboratory
        # 3. Repeatability, including both Coriolis flow meter to be calibrated and reference measurements.
        u_calib = (self.get_calibration_deviation_std(massflow) ** 2 +
                   self.get_calibration_reference_std(massflow) ** 2 +
                   self.get_calibration_repeatability(massflow) ** 2) ** 0.5
        return u_calib # Convert to relative uncertainty

    def calculate_relative_uncertainty(self, massflow):
        #The uncertainty for a flow calibrated coriolis mass flow meter consists of two contributions:
        #1. Calibration uncertainty
        #2. Field uncertainty
        if massflow == 0:
            return 0
        else:
            uncertainty_cal_dev = (self.get_calibration_deviation_std(massflow) / massflow) ** 2
            uncertainty_cal_ref = (self.get_calibration_reference_std(massflow) / massflow) ** 2
            uncertainty_cal_rept = (self.get_calibration_repeatability(massflow) / massflow) ** 2

            uncertainty_field_rept = (self.get_field_repeatability_std(massflow) / massflow) ** 2
            uncertainty_field_cond = (self.get_field_condition_std(massflow) / massflow) ** 2

            total_relative_uncertainty = np.square(uncertainty_cal_dev + uncertainty_cal_ref + uncertainty_cal_rept +
            uncertainty_field_rept + uncertainty_field_cond)
            return total_relative_uncertainty