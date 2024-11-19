# src/optimizer.py
import torch
from neuromancer.solvers import GradientSolver

class MultiZoneOptimizer:
    def __init__(self, model):
        self.model = model
        
    def optimize(self, forecast_data):
        # Create optimization problem
        problem = self.model.create_problem(forecast_data)
        
        # Initialize solver
        solver = GradientSolver(
            problem=problem,
            optimizer_class=torch.optim.Adam,
            optimizer_kwargs={'lr': 0.01}
        )
        
        # Solve optimization problem
        solution = solver.solve(
            num_iterations=1000,
            parameters=forecast_data
        )
        
        return solution