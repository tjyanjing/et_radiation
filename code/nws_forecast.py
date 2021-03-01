# nws_forecast:
# Functions include:
# nws forecast script extract weather forecasting information from the National Weather Service
# export the datasets with a format that is consistent to machine learning model build in this study
# plot the maximum, minimum temperature and forecasted net radiation

# TO DOs:
# Interacive plots (net rad vs time with hourly updates)
# Think about mapping it not just Merced, but mapping using a grid and heatmap

import requests
import pandas as pd
import datetime
import ERA5_process 
import time
import scaler
import class_model
from class_model import model
import joblib
import matplotlib.pyplot as plt
import geocoder


class forecast:
    def __init__(self, city='Merced, CA', model_type="lm"): # default location: Merced, CA
        import geocoder
        g = geocoder.arcgis(city)       
        self.lat = str(g.lat)
        self.lon = str(g.lng)
        self.dates = None
        self.location = None
        self.model_type = model_type
        self.model_id = None
        self.pred_time = None
        self.out_rad = None
        self.out_final = None

    
    # return a dataframe includes doy, lat, lon, T_max, T_min, T_avg, T_rng, doy
    def request_nws(self):    
        # request hourly temperature forecase from national weather service
        url = 'https://api.weather.gov/points/'+self.lat+','+self.lon
        r = requests.get(url)
        
        city = r.json()['properties']['relativeLocation']['properties']['city']
        state = r.json()['properties']['relativeLocation']['properties']['state']
        self.location = city + ", " + state
                
        r2 = requests.get(r.json()['properties']['forecastHourly'])

        out = pd.DataFrame(columns=['lat','lon','year','month','day','hour', 'date', 'doy','temp'])
        for i in range(len(r2.json()['properties']['periods'])):
            lat = self.lat
            lon = self.lon
            time = datetime.datetime.strptime(r2.json()['properties']['periods'][i]['startTime'][:-6], '%Y-%m-%dT%H:%M:%S')
            year = time.year
            month = time.month
            day = time.day
            hour = time.hour
            date = time.date()
            doy = time.timetuple().tm_yday
            temp = r2.json()['properties']['periods'][i]['temperature']
            temp = (temp-32)*5/9
            out.loc[i] = [lat, lon, year, month, day, hour, date, doy, temp]
            
        dates = out['date'].unique()
        self.dates = dates

        out = out.groupby(['doy'],as_index=False,group_keys=False).agg({'temp':['max','min','mean']})
        out.columns = ['doy','T_max','T_min','T_avg']
        out['T_rng'] = out['T_max'] - out['T_min']
        out.insert(1, "lat", self.lat) 
        out.insert(2, 'lon', self.lon)
        out[['lat','lon']] = out[['lat','lon']].astype(float)    
                
        # add the elevation and theoretical radiation      
        ERA5_process.process.elevation_function(out,'lat','lon')
        out_elev = ERA5_process.process(out)
        out_rad = out_elev.add_radiation()
        
        self.out_rad = out_rad
        
    
    def export_forecast(self):      
        # scaled the inputs to model
        df_non_scaled = self.out_rad[['lat', 'lon', 'elev_m', 'T_max', 'T_min', 'T_avg', 'T_rng', 'day_len_hr', 'rad_avg_W_sqm', 'rad_std_W_sqm', 'rad_max_W_sqm', 'rad_tot_J_sqm']]
        out_scaler = scaler.scaler_class(df_non_scaled)
        df_scaled = out_scaler.scale_out()
        
        # load model and predict
        from class_model import model
        loaded_model = joblib.load('./model_trained/2018/'+ self.model_type +'-rad_t_2018.sav')
        self.model_id = loaded_model.model_id
        
        df_out = self.out_rad
        start = time.time()
        df_out['forecast_J_d_sqm'] = loaded_model.predict(df_scaled)
        end = time.time()
        self.pred_time = round((end - start)/60,4)
        df_out = df_out.set_index(self.dates)
        
        self.out_final = df_out        
        return df_out
    
    def plot_forecast(self):
        fig, ax1 = plt.subplots()
        fig.suptitle(self.location, fontsize=20)

        color = 'tab:red'
        ax1.set_xlabel('Dates')
        ax1.set_ylabel('Net Radiation ($J~d^{-1}~m^{-2}$)', color=color)
        ax1.plot(self.out_final['forecast_J_d_sqm'], '-o', color=color, label='Net Radiation')
        ax1.tick_params(axis='y', labelcolor=color)
        plt.xticks(rotation=45)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color = 'tab:blue'
        ax2.set_ylabel('Temperature ($\circ$C)', color=color)  # we already handled the x-label with ax1
        ax2.plot(self.out_final['T_max'], '--v', color=color, label='T_max')
        ax2.plot(self.out_final['T_min'], '--^', color=color, label='T_min')
        ax2.tick_params(axis='y', labelcolor=color)

        fig.legend(loc='upper left',bbox_to_anchor=(0.2, 0.92),ncol=3)

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
        
        
        

