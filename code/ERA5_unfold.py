# ERA5_unfold:
# ERA5 unfold script processes the cdf raw files into dataframe
# select the 24hour maximum, minimum, and average temperature from customized geographysical locations (default loation: Merced, CA)
# export a dataframe with variables of'time','lat','lon','T_max','T_min','T_avg' (temperature in centi degree) 

# TODO: add ERA5 API inside the unfold function

import os
import numpy as np
import pandas as pd
import netCDF4
from netCDF4 import num2date  

class unfold_class:  
    def __init__(self,month='01',lat=37.30216,lon=-120.48297):
        self.month=month
        self.lat = lat
        self.lon = lon
        
    @staticmethod         
    def file_type(month, type): # read the list of cdf files 
        import os
        import numpy as np
        file_list =os.listdir('../data/ERA5')
        mask = [ ((string[55:61]=='2019'+month)|(string[56:62]=='2019'+month))&(type in string) for string in file_list]
        file_type =np.array(file_list)[mask]
        file_type =np.sort(file_type)
        return file_type
    
    def unfold(self, f): # unfold the cdf files to dataframes
        import numpy as np
        import pandas as pd
        import netCDF4
        from netCDF4 import num2date     
        
        nm_var = list(f.variables.keys())[3]
        t2m = f.variables[nm_var]
        
        # Get dimensions assuming 3D: time, latitude, longitude
        time_dim, lat_dim, lon_dim = t2m.get_dims()
        time_var = f.variables[time_dim.name]
        times = num2date(time_var[:], time_var.units)
        latitudes = f.variables[lat_dim.name][:]
        longitudes = f.variables[lon_dim.name][:]

        times_grid, latitudes_grid, longitudes_grid = [
        x.flatten() for x in np.meshgrid(times, latitudes, longitudes, indexing='ij')]
        df = pd.DataFrame({
            'time': [t.isoformat() for t in times_grid],
            'latitude': latitudes_grid,
            'longitude': longitudes_grid,
            't2m': t2m[:].flatten()})
        
        df = df[(abs(df['latitude']-self.lat)<=0.25) & (abs(df['longitude']-(self.lon))<=0.25)]
        return df
    
    def cbind(self):
        import pandas as pd
        import netCDF4
        print('Compile in Month:'+self.month)
        file_max = netCDF4.Dataset('../data/ERA5/'+self.file_type(self.month,'Max')[0])
        file_min = netCDF4.Dataset('../data/ERA5/'+self.file_type(self.month,'Min')[0])
        file_mean = netCDF4.Dataset('../data/ERA5/'+self.file_type(self.month,'Mean')[0])
        df_max=self.unfold(file_max)
        df_min=self.unfold(file_min)
        df_avg=self.unfold(file_mean)
        df_t2m = pd.concat([df_max,df_min['t2m'],df_avg['t2m']],axis=1)
        df_t2m.columns = ['time','lat','lon','T_max','T_min','T_avg']
        df_t2m[['T_max','T_min','T_avg']] = df_t2m[['T_max','T_min','T_avg']]-273
        print('Finished')
        return df_t2m
        



