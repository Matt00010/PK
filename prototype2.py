import matplotlib.pylab as plt
import numpy as np
import scipy.integrate

class Model:
    def __init__(self, name, Q_p1, V_c, V_p1, CL, X):
        self.name = name
        self.Q_p1 = Q_p1
        self.V_c = V_c
        self.V_p1 = V_p1
        self.CL = CL
        self.X = X

    def dose(self, t):
        return self.X

    def two_compartment(self, t, y):
        q_c, q_p1 = y
        transition = self.Q_p1 * (q_c / self.V_c - q_p1 / self.V_p1)
        dqc_dt = self.dose(t) - q_c / self.V_c * self.CL - transition
        dqp1_dt = transition
        return [dqc_dt, dqp1_dt]

    def three_compartment(self, )
    
    def plot_solution(self, t_eval, y0):
        sol = scipy.integrate.solve_ivp(
            fun=lambda t, y: self.rhs(t, y),
            t_span=[t_eval[0], t_eval[-1]],
            y0=y0, t_eval=t_eval
        )
        plt.plot(sol.t, sol.y[0, :], label=self.name + '- q_c')
        plt.plot(sol.t, sol.y[1, :], label=self.name + '- q_p1')



