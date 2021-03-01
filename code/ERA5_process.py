# ERA5_process:
# The ERA5 process script process the raw data from the ERA5_unfold script or CIMIS and AZMET monitoring dataset
# This requires an input dataframe generated from the ERA5 file or CIMIS and AZMET monitorning dataset

# Functions include:
# elevation_function: add elevation
# add_yest: add temperature from yesterday
# radiation: add theoretical calculation of day length and radiation 


class process:
    def __init__(self,df):
        self.df = df       
        
    # add elevation to lat, lon based on USGS map
    @staticmethod
    def elevation_function(df, lat_column, lon_column):
        import requests
        import urllib
        # USGS Elevation Point Query Service
        url = r'https://nationalmap.gov/epqs/pqs.php?'
        
        df = df
        lat_column = 'lat'
        lon_column = 'lon'
        
        
        """Query service using lat, lon. add the elevation values as a new column."""
        elevations = []
        for lat, lon in zip(df[lat_column], df[lon_column]):

            # define rest query params
            params = {
                'output': 'json',
                'x': lon,
                'y': lat,
                'units': 'Meters'
            }

            # format query string and return query value
            result = requests.get((url + urllib.parse.urlencode(params)))
            elevations.append(result.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation'])

        df.insert(3,'elev_m',elevations)
        
        return df

    # add temperature from yestdays
    def add_yest(self):
        import pandas as pd
        df = self.df
        
        # add date and doy
        time_date = pd.to_datetime(df['time']).dt.date
        df.insert(1,'date',time_date)
        time_doy = pd.to_datetime(df['time']).dt.dayofyear
        df.insert(2,'doy',time_doy)

        # calculate average T_max, T_min and T_avg at the same doy from each site
        df_v2 = df.groupby(['date','doy','lat','lon','elev_m'], as_index=False).mean()
        df_v2['T_rng'] = df_v2['T_max'] - df_v2['T_min']
        df_v2

        # sort by both lat and lon and then reset index
        df_v2 = df_v2.sort_values(by=['lat','lon'],ignore_index=True)
        df_v2

        # shift to get the T_yest
        df_yest = df_v2.shift(periods=1)[['T_max','T_min','T_avg']]
        df_yest.columns = ['T_max_yest', 'T_min_yest', 'T_avg_yest']
        df_yest

        # conbine the T and T_yest
        # remove all dates of 01/01
        df_v2 = pd.concat([df_v2,df_yest],axis=1)
        df_v2 = df_v2[df_v2.doy!=1]
        df_v2
        
        self.df=df_v2
        return df_v2
    
    # calculate theoretcial radiation
    @staticmethod
    def radiation(lat,elev,doy):
        import math
        import numpy as np
        
        slope = 0

        # a. SOLAR CONSTANTS
        G_sc = 1367 # Solar Constant W/m^2
        G_on = G_sc * ( 1 + 0.033 * math.cos(2*math.pi*doy/365))

        # a. Definitions
        # varphi = latitude
        # doy    = day of year
        # elev   = elevation in m
        # beta   = slope due south (in northern hemisphere is +ve)

        # b. INPUT CONVERSIONs
        varphi = lat * math.pi/180
        beta   = slope * math.pi/180

        # INTERNAL VARIABLES
        # delta = declination angle
        # L     = lognitude
        # omega = hour angle
        # hs    = sun altitude
        # gamma = solar azimuth

        time_interval = 1/60 #hr

        std_time = np.arange(0, 24 + time_interval, time_interval)
        std_time_sec = std_time * 24 * 60 * 60

        # c. Declination Angle
        delta = 23.45 * math.pi * math.sin(2*math.pi*(284+doy)/365)/180

        # d. HOUR Angle
        B = (doy-1) * 360/365
        E = 229.2 * (0.000075 
                     + 0.001868 * math.cos(B) 
                     - 0.032077 * math.sin(B) 
                     - 0.014615 * math.cos(2*B) 
                     - 0.040890 * math.sin(2*B)
                    )
        slr_time = std_time + E/60
        omega = math.pi * 15 * (slr_time-12)/180

        # e. Incidence Angle
        cos_theta = np.cos(varphi-beta) * np.cos(delta) * np.cos(omega) + np.sin(varphi-beta) * np.sin(delta) # Northern Hemisphere
        # cos_theta = math.cos(varphi+beta) * math.cos(delta) * math.cos(omega) + math.sin(varphi+beta) * math.sin(delta) # Southern Hemisphere

        cos_theta_z = np.cos(varphi) * np.cos(delta) * np.cos(omega) + np.sin(varphi) * np.sin(delta) 

        # f. Sun Altitude
        # g. Day length
        N = (180/math.pi) * 2 * math.acos(-math.tan(varphi)*math.tan(delta))/15

        # h. Extra Terrestial Radiation
        G_o = G_on * cos_theta
        G_o[G_o<0] = np.NAN

        # i. Ground Surface Radiation
        # Eq(7) from Remote Sens. 2013, 5, 4735-4752; doi:10.3390/rs5104735
        tau = (0.75 + 2e-5 * elev)
        G_c = tau * G_o

        G_c[G_c<0] = np.NAN

        G_o_tot = sum(G_o[~np.isnan(G_o)]) * time_interval * 60 * 60
        G_c_tot = sum(G_c[~np.isnan(G_c)]) * time_interval * 60 * 60

        # outputs
        day_len = N
        rad_avg = np.mean(G_c[~np.isnan(G_c)])
        rad_sd  = np.std(G_c[~np.isnan(G_c)])
        rad_max = np.max(G_c[~np.isnan(G_c)])
        rad_tot = G_c_tot

        return day_len, rad_avg, rad_sd, rad_max, rad_tot
    
    # add theoretical radiaion
    def add_radiation(self):
        import pandas as pd
        df_v2 = self.df
        df_radiation = pd.DataFrame(df_v2.apply( lambda X: self.radiation(X['lat'], X['elev_m'], X['doy']), axis=1).to_list(),
                 columns=['day_len_hr', 'rad_avg_W_sqm', 'rad_std_W_sqm', 'rad_max_W_sqm', 'rad_tot_J_sqm'])
        df_radiation = df_radiation.set_index(df_v2.index)
        
        df_v3 = pd.concat([df_v2, df_radiation], axis=1)  
        self.df = df_v3
        return df_v3

            
       