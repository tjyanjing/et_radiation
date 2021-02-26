# Machine-learning Based Net Radiation Forecaster 

## Overview
This repository was created for the machine-learning forecasters that predict net radiation using minimum weather information, e.g., temperature. It pulls data from the [National Weather Service (NWS) API](https://www.weather.gov/documentation/services-web-api) for customized location and forecasts the net radiation.

## Features
* The model built was based on five popular machine learning algorithms, including multi-linear regression, K nearest neighbor, support vector machine, random forests, and gradient boosted tree regression.
* The dataset for model construction was collected from the [CIMIS](https://cimis.water.ca.gov/Default.aspx) and [AZMET](https://cals.arizona.edu/AZMET/) from 1982 to 2018.
* Extracting [ERA5](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) reanalysis global climate dataset for forecast validation.
* Forecasting 7-day net radiation from the running date after automatically extracting weather forecasting information from NWS.

![Map of Radiation Stations](./figs/fig_demo_01.png =250x "Map of Radiation Station")

## Running The Forecaster

```
import nws_forecast
from nws_forecast import forecast

# request weather forecast from NWS
my_forecast = forecast(city="Merced, CA", model_type ='lm')
my_forecast.request_nws()

# proceed the forecast and plot the forecast results
from class_model import model
my_forecast.export_forecast()
my_forecast.plot_forecast()
```
## Model Preview

![Prediction against measurement](./figs/fig_demo_02.png =250x "Prediction against measurement using one model.")

![Theoretical, predicated, and observed net radiation against time using a Gradient Boosted Tree Model at one station in California](./figs/fig_demo_03.png =250x "Theoretical, predicated, and observed net radiation against time at one location.")

![Net radiation forecasting at Merced, CA](./figs/fig_demo_04.png =250x "Net radiation forecasting at one location.")