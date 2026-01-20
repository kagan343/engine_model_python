import cantera as ct
import numpy as np

# Fuel mass flow calc function
def calc_fuel_mdot(m_dot_air, equivRatio):
    """
    Add/ change to cantera set equivalence ratio when have time so works for all fuel/ not manual
    """
    # For now manually doing propane
    # x = 3, y = 8  -> a = x + y/4 = 5
    # C3H8 + 5 O2 + 18.8 N2

    # Molecular weights [g/mol]
    M_O2 = 31.998
    M_N2 = 28.014
    M_C3H8 = 44.097

    mass_O2 = 5.0 * M_O2
    mass_N2 = 18.8 * M_N2
    mass_propane = 1.0 * M_C3H8

    # Air-to-fuel mass ratio (unitless)
    air_to_fuel = (mass_O2 + mass_N2) / mass_propane

    # Stoichiometric fuel mass flow
    m_dot_fuel_stoic = m_dot_air / air_to_fuel

    # Actual fuel mass flow (using equivalence ratio)
    m_dot_fuel = m_dot_fuel_stoic / equivRatio
    return m_dot_fuel


# Getter functions
def get_gamma(gas: ct.Solution) -> float:
    # gamma = cp/cv
    return gas.cp_mass / gas.cv_mass

def get_R(gas: ct.Solution) -> float:
    # gas constant
    return gas.cp - gas.cv

def get_a(gas: ct.Solution) -> float:
    # local speed of sound, a = sqrt(gamma*R*T)
    return np.sqrt(get_R(gas) * get_gamma(gas) * gas.T)

def get_P(p_static: float, gamma: float, mach: float) -> float:
    # stagnation pressure for isentropic process
    return p_static * ((1 + ((gamma - 1) / 2) * mach**2)**(gamma / (gamma - 1)))

def get_T(t_static: float, gamma: float, mach: float) -> float:
    # stagnation temperature for isentropic process
    return t_static * (1 + ((gamma - 1) / 2) * mach**2)

