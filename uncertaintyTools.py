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

    # Idemyldring.
    # Vurdere en egen klasse her som samler inn data? Evt fra notatblokk? Excel ark?
    # La oss si nokken skal bruke programmet, kor skal dei legge inn verdiane? 
    # Kanskje lage en 'excel' mal for å legge inn tall, den leser og legger alt inn her.


    ##################################################################################################################################
                        #Uncertainty tools
    #################################################################################################################################

    def convert_std_to_confidence(self, std_uncertainty):
        return self.k*std_uncertainty
    
    def linear_interpolation(self, flowrate, uncertainty):
        return np.interp(flowrate, self.flowrates_kg_hr, uncertainty)

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

    def calculate_field_sum_variance(self, flowrate):
        # Felt usikkerhet består av to kontribusjoner:
        # Repeterbarhet til flowmeter under felt kondisjoner
        # Usikkerhet til endring av forhold fra flow kalibrasjon    til felt operasjon

        u_field = math.sqrt(self.get_field_repeatability_std(flowrate)**2 + self.get_field_condition_std(flowrate)**2)
        return u_field  # Convert to relative uncertainty

    ##################################################################################################################################
                        #Calibration uncertainty
    #################################################################################################################################

    def get_calibration_deviation_std(self, flowrate):
        # Calculated from deviation between coriolis mass flow rate and mass flow rate measured by reference ,eter. 
        # See appendix A in NFOGM handbook for calculation.
        
        #deviation = [1.2,0.55,0.3,0.23,0.18,0.2,0.24] # in percentage, (uncorrected)
        deviation = [0.145, 0.145, 0.145, 0.145, 0.145, 0.145, 0.145]
        linearized_deviation= self.linear_interpolation(flowrate,deviation)
        return linearized_deviation

    def get_calibration_reference_std(self, flowrate):
        # Kan  variere med flow.
        # Depends on metering equpiment used at flow laboratory, and will be found in calibration certificate. 
        # Can vary with flowrate.

        reference = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1] #In percentage, std
        linearized_reference= self.linear_interpolation(flowrate, reference)
        return linearized_reference

    def get_calibration_repeatability_std(self, flowrate):
        # Kan variere med flow.
        # This term covers repeatability of the Coriolis flow meter to be calibrated and the reference measurement.
        # This varies with flow rate - use linear interpolation between points.
        
        repeatability = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05] #In percentage
        linearized_repeatability= self.linear_interpolation(flowrate, repeatability)
        return linearized_repeatability

    def calculate_calibration_sum_variance(self, flowrate):
        # Calibration uncertainty for a calibrated coriolis mass flowmeter consists of 3 contributions:
        # 1. Uncertainty of correction factor estimate
        # 2. Uncertainty of reference measurement at flow laboratory
        # 3. Repeatability, including both Coriolis flow meter to be calibrated and reference measurements.

        
        u_calib = self.get_calibration_deviation_std(flowrate)**2 + self.get_calibration_repeatability_std(flowrate)**2 + self.get_calibration_reference_std(flowrate)**2
        return u_calib


    def calculate_relative_uncertainty(self, flowrate):
        #The uncertainty for a flow calibrated coriolis mass flow meter consists of two contributions:
        #1. Calibration uncertainty
        #2. Field 
        
        if flowrate == 0:
            return 0
        else:
            #Sum of variances. In %**2
            sum_of_variance = self.calculate_calibration_sum_variance(flowrate) + self.calculate_field_sum_variance(flowrate)
            relative_combined_std_uncertainty = math.sqrt(sum_of_variance)
            realtive_expanded_uncertainty = self.convert_std_to_confidence(relative_combined_std_uncertainty)
            return realtive_expanded_uncertainty


    ##################################################################################################################################
                        #Combining uncertainty
    #################################################################################################################################
        
    def total_combined_uncertainty(self, time_increments, uncertaintyarray):
        total_uncertainty = 0
        for uncertainty in uncertaintyarray:
            uncertainty_contribution = uncertainty*time_increments
            total_uncertainty += uncertainty_contribution
        #Bedre modularitet om å gange inn "time increments" til slutt etter for løkke? Sida
        #E(deltaT * q_mi) -> deltaT E(q_mi)
        return total_uncertainty #Total usikkerhet for heile fylling.


  ##################################################################################################################################
                        # Flow calculation uncetainty
  #################################################################################################################################
    def calculate_std_vol_flowrate_uncertainty(self, qvo, qm, uqm, z0m, uz0m):
        u_qv0 = math.sqrt((uqm/qm)**2+(uz0m/z0m)**2)*qvo
        return u_qv0








def run(flowrate):
    uncertainty = uncertaintyTools().calculate_relative_uncertainty(flowrate)
    print(uncertainty)
run(9235)
