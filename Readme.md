taskResilience.py uses the NumPy library to create a grid of data points and calculates task resilience value R based on a conditional formula involving task capacity tc and interruption probability p. It then uses Matplotlib to create and display a 3D surface plot of R as a function of tc and p, illustrating how "Task Resilience" changes with "Task Capacity" and "Interruption Probability".

counterPlotResilience.py calculates the task resilience value R over a 2D grid and visualizes the result as a colored contour map, illustrating how "Task Resilience" changes with "Task Capacity" and "Interruption Probability".

data.xlsx involves the parameters of UAV's configuration and the parameters of target unit's configuration used in simulation.

uavAllocation112230211.py : An object-oriented approach was employed to formulate a problem model encompassing Unmanned Aerial Vehicles (UAVs), their payloads, and designated task areas. This model incorporates an interruption probability model, a resilience model, and a UAV cost matrix to calculate an optimal allocation scheme for a UAV swarm, ensuring mission requirements are met in the presence of probabilistic interruptions.