import numpy as np
from utils.base_solver import *
from utils.matrices import *
from utils.measures import *
from utils.plotting import *

# TODO
# what is no BC?
# physical interpretation in temperatures

class HeatSolverResult(BaseSolverResult):
    def __init__(self, t_values, u_values):
        super().__init__(u_values)
        self.t_values = t_values

class HeatSolver(BaseSolver):
    def __init__(self, points, faces, boundary, dt=0.1, num_iterations=10, matrices=None):
        super().__init__(points, faces, boundary, matrices=matrices)
        self.dt = dt
        self.num_iterations = num_iterations

    def solve(self, u_initial, robin_bc=None, load_function=None):
        print('Solving heat equation...')
        load_function = load_function if load_function is not None else lambda x: 0
        b = assemble_vector(self.points, self.faces, calculate_element_load_vector, load_function)
        K_temp = self.K.copy()
        if robin_bc is not None:
            W, g_D, g_N = robin_bc
            R = assemble_matrix(self.points, self.boundary, calculate_element_boundary_mass_matrix, W)
            r = assemble_vector(self.points, self.boundary, calculate_element_boundary_load_vector, 
                                lambda x: W(x) * g_D(x) + g_N(x))
            K_temp += R
            b += r

        u = u_initial

        t_values = [0]
        u_values = [u_initial]
        print(f't = {t_values[0]:.3f}, mean temp = {calculate_mean_value(self.points, self.faces, u_initial):.3f}')

        for i in range(self.num_iterations):
            # backwards Euler
            u = np.linalg.solve(self.M + K_temp * self.dt, self.M @ u + b * self.dt)
            t_values.append(self.dt * (i+1))
            u_values.append(u)
            print(f't = {t_values[-1]:.3f}, mean temp = {calculate_mean_value(self.points, self.faces, u_values[-1]):.3f}')

        self.result = HeatSolverResult(t_values, u_values)
        return self.result

    def plot_result(self, fixed_cbar=False):
        plot_colored_mesh_animation(self.points, self.faces, 
                                    self.result.t_values, self.result.u_values, 
                                    title='Heat Equation Simulation',
                                    cbar_label='Temperature', fixed_cbar=fixed_cbar)

    @classmethod
    def from_base_solver(cls, base_solver, dt=0.1, num_iterations=10):
        return cls(base_solver.points, base_solver.faces, base_solver.boundary, dt=dt, num_iterations=num_iterations, matrices=(base_solver.M, base_solver.K))