# scaling function
# the max-min is based on the whole dataset from CA and AZ (see df_max_min in section 1.3 in netrad_01.ipynb) 
# consider make that into a flexbile function calculating the max_min first then insert these values automatically
class scaler_class:
    def __init__(self, unscaled):
        self.unscaled = unscaled
        self.scaled = None
    
    @staticmethod
    def scale_variables(x):
        import numpy as np
        x_min = [  31,  # lat
                  -124, # lon
                  -61,  # elve_m
                  -8,  # T_max,
                  -40,  # T_min,
                  -13,  # T_avg,
                   -17,   # T_rng,
                  -8,  # T_max_yest,
                  -40,  # T_min_yest,
                  -13,  # T_avg_yest,
                   8,   # day_len_hr,
                  296,  # rad_avg_W_sqm,
                  137,  # rad_std_W_sqm,
                  454,  # rad_max_W_sqm,
                  9526925 # rad_tot_J_sqm
    #               0     # net_rad_tot_J_sqm
                ]
        x_max = [   42,   # lat
                    -109, # lon
                    2107, # elev_m,
                    53,   # T_max,
                    36,   # T_min,
                    42,   # T_avg,
                    79,   # T_rng,
                    53,   # T_max_yest,
                    36,   # T_min_yest,
                    42,   # T_avg_yest,
                    16,   # day_len_hr,
                    642,  # rad_avg_W_sqm,
                    323,  # rad_std_W_sqm,
                    1030, # rad_max_W_sqm,
                    32967081   # rad_tot_J_sqm
    #                 1     # net_rad_tot_J_sqm
                ]
        x_scaled = np.divide(np.subtract(x,x_min), np.subtract(x_max,x_min))
        return x_scaled
    
    @staticmethod
    def scale_variables_short(x):
        import numpy as np
        x_min = [  31,  # lat
                  -124, # lon
                  -61,  # elve_m
                  -8,  # T_max,
                  -40,  # T_min,
                  -13,  # T_avg,
                   -17,   # T_rng,
                   8,   # day_len_hr,
                  296,  # rad_avg_W_sqm,
                  137,  # rad_std_W_sqm,
                  454,  # rad_max_W_sqm,
                  9526925 # rad_tot_J_sqm
    #               0     # net_rad_tot_J_sqm
                ]
        x_max = [   42,   # lat
                    -109, # lon
                    2107, # elev_m,
                    53,   # T_max,
                    36,   # T_min,
                    42,   # T_avg,
                    79,   # T_rng,
                    16,   # day_len_hr,
                    642,  # rad_avg_W_sqm,
                    323,  # rad_std_W_sqm,
                    1030, # rad_max_W_sqm,
                    32967081   # rad_tot_J_sqm
    #                 1     # net_rad_tot_J_sqm
                ]
        x_scaled = np.divide(np.subtract(x,x_min), np.subtract(x_max,x_min))
        return x_scaled



    def scale_out(self):
        if self.unscaled.shape[1]>12:
            self.scaled = self.unscaled.apply(lambda x: self.scale_variables(x), axis=1)
        else:
            self.scaled = self.unscaled.apply(lambda x: self.scale_variables_short(x), axis=1)
        return self.scaled
        




