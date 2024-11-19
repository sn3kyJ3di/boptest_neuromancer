# src/client.py
import requests
import numpy as np
from datetime import datetime, timedelta

class BOPTestClient:
    def __init__(self, url="http://localhost:5000"):
        self.url = url
        self.step = 3600  # 1-hour timestep
        self.horizon = 24  # 24-hour prediction horizon
        
    def get_forecast(self):
        """Get forecast data from BOPTest"""
        response = requests.put(f"{self.url}/forecast")
        if response.ok:
            return response.json()
        else:
            raise Exception(f"Forecast request failed: {response.status_code}")
    
    def get_measurements(self):
        """Get current measurements"""
        response = requests.get(f"{self.url}/measurements")
        if response.ok:
            return response.json()
        else:
            raise Exception(f"Measurements request failed: {response.status_code}")
            
    def advance(self, control_inputs):
        """Advance simulation with control inputs"""
        response = requests.post(
            f"{self.url}/advance",
            json=control_inputs
        )
        if response.ok:
            return response.json()
        else:
            raise Exception(f"Advance request failed: {response.status_code}")