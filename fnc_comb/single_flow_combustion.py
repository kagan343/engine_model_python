
import cantera as ct
import numpy as np
from .help_fnc import *

def single_flow_combustion(eng, diff_gas_out, diff_mdot_out):

    # Set variables
    T_t3 = diff_gas_out.T
    P_t3 = diff_gas_out.P
    volume_b = eng.combustor.volume_b
    m_dot_air = diff_mdot_out
    m_dot_fuel = calc_fuel_mdot(m_dot_air, eng.combustor.equivRatio)

    # Calcuate P_t4 using estimated combustor pressure ratio
    P_t4 = P_t3 * eng.combustor.PR_b
    
    ### Cantera
    # Set up
    mech = "gri30.yaml"
    gas_air  = ct.Solution(mech)
    gas_fuel = ct.Solution(mech)
    gas_init = ct.Solution(mech)  # separate object for the reactor initial state

    # Compositions
    air_X  = "O2:0.21, N2:0.79" # air same comp always for this model
    fuel_X = eng.combustor.fuel_comp

    # Set inlet states
    gas_air.TPX  = T_t3, P_t4, air_X
    gas_fuel.TPX = T_t3, P_t4, fuel_X
    gas_init.TPX = 1200.0, P_t4, air_X

    # Reservoirs
    upstream_air = ct.Reservoir(gas_air)
    upstream_fuel = ct.Reservoir(gas_fuel)
    downstream = ct.Reservoir(gas_init) # "sink" reservoir; state doesn't feed back, can just use init object

    # Reactor
    r = ct.IdealGasReactor(gas_init) # initialized with gas_init
    r.volume = volume_b
    r.energy_enabled = True # ensure energy is on

    # Mass flow controllers
    mfc_air  = ct.MassFlowController(upstream_air, r)
    mfc_fuel = ct.MassFlowController(upstream_fuel, r)
    mfc_air.mass_flow_rate  = m_dot_air
    mfc_fuel.mass_flow_rate = m_dot_fuel

    # Valve to downstream, pressure dependent outlet device
    v = ct.Valve(r, downstream)
    v.valve_coeff = 1e-4
    # Can change to fix flow below for comparison
    # mfc_out = ct.MassFlowController(r, downstream)
    # mfc_out.mass_flow_rate = m_dot_air + m_dot_fuel

    # Reactor network + integrate
    network = ct.ReactorNet([r])

    t = 0.0
    dt = 1e-6

    rho0 = r.density
    vol = r.volume
    tau  = rho0 * vol / (m_dot_air + m_dot_fuel)
    t_end = 20.0 * tau

    # Check comp right after start (not a linear progression, just viewing solver at different txTau)
    network.advance(6.5*tau)
    gas_out = ct.Solution(mech)
    gas_out.TPY = r.T, r.thermo.P, r.thermo.Y
    X = gas_out.X              # mole fractions (numpy array)
    iCO2  = gas_out.species_index('CO2')
    iH2O  = gas_out.species_index('H2O')
    iO2   = gas_out.species_index('O2')
    ifuel = gas_out.species_index('C3H8')
    print("########## Before ############")
    print("Mole fractions at outlet:")
    print(f"  CO2  = {X[iCO2]:.6e}")
    print(f"  H2O  = {X[iH2O]:.6e}")
    print(f"  O2   = {X[iO2]:.6e}")
    print(f"  C3H8 = {X[ifuel]:.6e}")


    network.advance(t_end)  # advance(network, t_end)

    # Set gas_out properties, exporting mass fractions Y, T, P
    gas_out = ct.Solution(mech)
    gas_out.TPY = r.T, r.thermo.P, r.thermo.Y

    X = gas_out.X              # mole fractions (numpy array)

    iCO2  = gas_out.species_index('CO2')
    iH2O  = gas_out.species_index('H2O')
    iO2   = gas_out.species_index('O2')
    ifuel = gas_out.species_index('C3H8')

    print("########## After ############")
    print("Mole fractions at outlet:")
    print(f"  CO2  = {X[iCO2]:.6e}")
    print(f"  H2O  = {X[iH2O]:.6e}")
    print(f"  O2   = {X[iO2]:.6e}")
    print(f"  C3H8 = {X[ifuel]:.6e}")

    return gas_out