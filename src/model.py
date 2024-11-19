# src/model.py
import neuromancer as nm
import torch

class MultiZoneModel:
    def __init__(self, horizon=24):
        self.horizon = horizon
        self.zones = ['cor', 'eas', 'nor', 'sou', 'wes']
        
    def create_problem(self, forecast_data):
        # Create variables for each zone
        zone_temps = {
            zone: nm.variables.Variable(
                f"temp_{zone}",
                num_vars=self.horizon
            ) for zone in self.zones
        }
        
        # Create variables for HVAC control
        hvac_control = {
            zone: nm.variables.Variable(
                f"hvac_{zone}",
                num_vars=self.horizon
            ) for zone in self.zones
        }
        
        # Define constraints
        constraints = []
        
        # Temperature constraints
        for zone in self.zones:
            constraints.extend([
                # Temperature bounds
                nm.constraints.InequalityConstraint(
                    lambda x: x - 26,  # Max temp (°C)
                    variables=[zone_temps[zone]],
                    name=f"max_temp_{zone}"
                ),
                nm.constraints.InequalityConstraint(
                    lambda x: 20 - x,  # Min temp (°C)
                    variables=[zone_temps[zone]],
                    name=f"min_temp_{zone}"
                ),
                
                # HVAC control bounds
                nm.constraints.InequalityConstraint(
                    lambda x: x - 1.0,  # Max control
                    variables=[hvac_control[zone]],
                    name=f"max_hvac_{zone}"
                ),
                nm.constraints.InequalityConstraint(
                    lambda x: 0.0 - x,  # Min control
                    variables=[hvac_control[zone]],
                    name=f"min_hvac_{zone}"
                )
            ])
        
        # Define objective function
        def objective_fn(temps, hvac, forecasts):
            energy_cost = sum(
                hvac[zone] * forecasts['PriceElectricPowerDynamic']
                for zone in self.zones
            )
            
            comfort_cost = sum(
                torch.abs(temps[zone] - 23.0) * forecasts[f'Occupancy[{zone}]']
                for zone in self.zones
            )
            
            return energy_cost + 10.0 * comfort_cost
        
        objective = nm.objectives.Objective(
            objective_fn,
            variables=[zone_temps, hvac_control, forecast_data]
        )
        
        return nm.Problem(
            variables=list(zone_temps.values()) + list(hvac_control.values()),
            objectives=[objective],
            constraints=constraints
        )