# src/data_handler.py
import numpy as np
import pandas as pd

class DataHandler:
    def __init__(self):
        self.required_forecasts = [
            'TDryBul',           # Outside air temperature
            'HDirNor',           # Solar radiation
            'relHum',            # Relative humidity
            'winSpe',            # Wind speed
            'Occupancy[cor]',    # Occupancy forecasts
            'Occupancy[eas]',
            'Occupancy[nor]',
            'Occupancy[sou]',
            'Occupancy[wes]',
            'PriceElectricPowerDynamic'  # Energy prices
        ]
        
    def process_forecasts(self, forecast_data):
        """Process raw forecast data into format for Neuromancer"""
        processed_data = {}
        
        for key in self.required_forecasts:
            if key in forecast_data:
                processed_data[key] = np.array(forecast_data[key])
            else:
                raise KeyError(f"Required forecast {key} not found in data")
                
        # Convert temperatures from Kelvin to Celsius
        if 'TDryBul' in processed_data:
            processed_data['TDryBul'] = processed_data['TDryBul'] - 273.15
            
        return processed_data