"""
    def generate_simulation_mean_minutes(self):
        
        This method generates flow rates similar to those seen in a HRS, in the
        form of kg/minute. It has 3 stages, increase, mass_flowrate_top, and 
        decline.  
        for flow_rate in range(0, 37):  # Assuming increments of 0.1 for 0 to 3.6
            # print(f"Flow Rate: {flow_rate / 10} kg/s")
            # time.sleep(0.1)
            self.massflows.append(flow_rate / 10)

        # Keep steady flow rate at 3.6 for a duration (e.g., 10 seconds)
        for _ in range(100):
            # print("Flow Rate: 3.6 kg/s")
            # time.sleep(0.1)
            self.massflows.append(flow_rate / 10)

        # Decrease flow rate from 3.6 back to 0
        for flow_rate in range(36, -1, -1):  # Assuming decrements of 0.1 for 3.6 to 0
            # print(f"Flow Rate: {flow_rate / 10} kg/s")
            # time.sleep(0.1)
            self.massflows.append(flow_rate / 10)
        return self.massflows
        """
