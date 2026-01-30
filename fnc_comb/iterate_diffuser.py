
import cantera as ct
import numpy as np
from .help_fnc import *


def iterate_diffuser(eng):
# Iterate gas velocity at combustor inlet (diffuser outlet) until convergence

    # For seeing variables easier, list here
    m_dot = eng.m_dot_air
    A_in = eng.diffuser.A_diff_in
    A_out = eng.diffuser.A_diff_out
    eta_i = eng.diffuser.diff_eta_i
    gas_in = eng.diff_gas_in
    gas_out = eng.diff_gas_out

    # Loop control
    tol = 0.01 # tolerance for convergence
    max_iter = 100
    converged = False # convergence boolean
    n_iter = 0 # iteration tracker

    # Calc input gas properties
    v_in = m_dot / (gas_in.density * A_in) # inlet vel. = m_dot/rho*A
    M_in = v_in / get_a(gas_in) # inlet mach number
    gamma_in = get_gamma(gas_in)
    T_0in = get_T(gas_in.T, gamma_in, M_in)
    P_0in = get_P(gas_in.P, gamma_in, M_in)

    #print(f'T_0in_init = {T_0in}')
    # print(f'v_in_init = {v_in}')
    # #print(f'M_in_init = {M_in}')
    # print(f'stagnation pressure P_0in = {P_0in}')
    # print(f'static pressure P_in = {gas_in.P}')

    # Set initial guesses using wanted outlet area
    T_0out = T_0in # 0 = stagnation/ total
    v_out_guess = m_dot / (gas_in.density * A_out) # utilize outlet area
    gamma_out = gamma_in
  
    while not converged and n_iter <= max_iter:
        # Calc properties using current guess
        # no work done, adiabatic
        # 1 - static temp out from temperatur energy balance from inlet to outlet
        #   - diffsuer stagnation temp and static can be assumed same due to no work and adiabatic
        T_out = gas_in.T + (v_in**2 / (2 * gas_in.cp) - v_out_guess**2 / (2 * gas_out.cp))
        # 2 - total/ stagnation pressure from energy balance utilizing efficiency of diffuser
        P_0out = gas_in.P * (1 + eta_i * v_in**2 / (2 * gas_in.cp * gas_in.T))**(gamma_in / (gamma_in - 1))
        # 3 - relate stagnation/total pressure to static pressure at outlet
        P_out = P_0out * (T_out / T_0out)**(gamma_out / (gamma_out - 1))

        # Update gas with new properties
        gas_out.TP = T_out, P_out
        gamma_out = get_gamma(gas_out) # Grab after T and P updated

        # Update velocity
        v_out = v_out_guess
        v_out_guess = m_dot / (gas_out.density * A_out)

        if abs(v_out - v_out_guess) < tol:# and n_iter > 20:
            # print(f"Diffuser exit velocity converged, niter={n_iter}")
            converged = True
            M_out = v_out_guess / get_a(gas_out) # Set mach using last iteration values
            m_dot_out = v_out_guess * (gas_out.density * A_out) # Check for same value
            # print(f"v_out = {v_out}")
            # print(f"m_dot_out = {m_dot_out}")
            # print(f"stangation P_0out = {P_0out}, static P_out = {P_out}")
        elif n_iter < max_iter:
            n_iter += 1
        else:
            M_out = 0
            print(f"Diffuser exit velocity NOT converged, niter={n_iter}")

    return M_out, converged, gas_out, m_dot_out

