from src.client import BOPTestClient
from src.data_handler import DataHandler
from src.model import MultiZoneModel
from src.optimizer import MultiZoneOptimizer


def main():
    # Initialize components
    client = BOPTestClient()
    data_handler = DataHandler()
    model = MultiZoneModel()
    optimizer = MultiZoneOptimizer(model)
    
    # Simulation loop
    simulation_steps = 24 * 7  # One week simulation
    
    for step in range(simulation_steps):
        # Get forecasts
        forecast_data = client.get_forecast()
        processed_forecasts = data_handler.process_forecasts(forecast_data)
        
        # Optimize control strategy
        solution = optimizer.optimize(processed_forecasts)
        
        # Extract control actions for current timestep
        control_actions = {
            f"hvac_{zone}": solution[f"hvac_{zone}"][0].item()
            for zone in model.zones
        }
        
        # Apply control actions
        client.advance(control_actions)
        
    print(f"Step {step}: Control actions applied")
    


if __name__ == "__main__":
    main()