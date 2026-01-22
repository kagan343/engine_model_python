
import cantera as ct
import numpy as np
from .help_fnc import *

def multi_flow_recirculation_combustion(eng, diff_gas_out, diff_mdot_out):

    # Set variables
    T_t3 = diff_gas_out.T
    P_t3 = diff_gas_out.P
    volume_b = eng.combustor.volume_b
    f_primary = eng.combustor.f_primary
    v_frac_primary = eng.combustor.v_frac_primary


    # Calcuate P_t4 using estimated combustor pressure ratio
    P_t4 = P_t3 * eng.combustor.PR_b
    
    # Total mass flows
    m_dot_air_total = diff_mdot_out
    m_dot_fuel = calc_fuel_mdot(m_dot_air_total, eng.combustor.equivRatio)
    print(f"eng.combustor.equivRatio = {eng.combustor.equivRatio}")

    # Split air, fraction can be dictated by geometry of chamber
    m_dot_air_primary = f_primary * m_dot_air_total
    m_dot_air_secondary = (1-f_primary) * m_dot_air_total

    # Split volume
    v_primary = v_frac_primary * volume_b
    v_secondary = (1-v_frac_primary) * volume_b


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
    gas_init.TPX = 1200.0, P_t4, air_X # 1200 guess to help solver converge

    # Reservoirs
    upstream_air = ct.Reservoir(gas_air)
    upstream_fuel = ct.Reservoir(gas_fuel)
    downstream = ct.Reservoir(gas_init) # "sink" reservoir; state doesn't feed back, can just use init object



    ##### Primary reactor #####
    r1 = ct.IdealGasReactor(gas_init) # initialized with gas_init
    r1.volume = v_primary
    r1.energy_enabled = True # ensure energy is on

    # Primary reactor mass flow controllers (fuel only into primary zone)
    mfc_air1  = ct.MassFlowController(upstream_air, r1)
    mfc_fuel = ct.MassFlowController(upstream_fuel, r1)
    mfc_air1.mass_flow_rate  = m_dot_air_primary
    mfc_fuel.mass_flow_rate = m_dot_fuel


    ##### Secondary reactor #####
    r2 = ct.IdealGasReactor(gas_init) # initialized with gas_init
    r2.volume = v_secondary
    r2.energy_enabled = True # ensure energy is on

    # Secondary reactor flow from primary reactor, pressure valve
    valve12 = ct.Valve(r1, r2)
    valve12.valve_coeff = 1e-4

    # Secondary reactor mass flow controller from upstream air
    mfc_air2  = ct.MassFlowController(upstream_air, r2)
    mfc_air2.mass_flow_rate  = m_dot_air_secondary


    # Valve from r2 to downstream, pressure valve
    # see sketch in notebook if forget set up flow
    v = ct.Valve(r2, downstream)
    v.valve_coeff = 1e-4

    # Reactor network and set times
    network = ct.ReactorNet([r1, r2])
    t = 0.0
    dt = 1e-6


    # Find primary zone tau
    rho1 = r1.density
    vol1 = r1.volume
    tau1  = rho1 * vol1 / (m_dot_air_primary + m_dot_fuel)
    # Find seconary zone tau
    rho2 = r2.density
    vol2 = r2.volume
    tau2 = rho2 * vol2 / (m_dot_air_total + m_dot_fuel)

    # Utilize slowest time / max tau to ensure network fully settles
    # t_end = 20.0 * max(tau1, tau2)
    # network.advance(t_end)  # advance(network, t_end)

    network.advance_to_steady_state()

    # Set gas_out properties, exporting mass fractions Y, T, P
    gas_out = ct.Solution(mech)
    gas_out.TPY = r2.T, r2.thermo.P, r2.thermo.Y

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