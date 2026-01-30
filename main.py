
# Main engine scripts
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from dataclasses import dataclass
import cantera as ct # global python is what installed cantera, 3.12.4
import combustor_main as comb
# Util
from pickle_util import save, load
from plot_util import plot_vol_f, plot_3D_scatter, plot_min_ignition_layer



@dataclass
class DiffuserCfg:
    A_diff_in: float
    A_diff_out: float
    diff_eta_i: float

@dataclass
class CombustorCfg:
    fuel_comp: str
    PR_b: float
    n_b: float
    primary_equivRatio: float  
    volume_b: float
    f_primary: float # Fraction of primary air mass flow in chamber
    v_frac_primary: float # Fraction of primary air volume of total chamber volume

# temporary - value from matlab of compressor outlet
class Engine():
    def __init__(
        self,
        T_t3: float,
        P_t3: float,
        m_dot_air: float,

        diffuser: DiffuserCfg,
        combustor: CombustorCfg,
    ):
        self.T_t3 = T_t3
        self.P_t3 = P_t3
        self.m_dot_air = m_dot_air

        self.diffuser = diffuser
        self.combustor = combustor

        # Can just set gas object meches here since all the same for now, and props assigned in fncs
        self.diff_gas_in = ct.Solution("gri30.yaml")
        self.diff_gas_out = ct.Solution("gri30.yaml")





if __name__ == "__main__":
    # Units: Kelvin, Pascla, meters(m^2,m^3)
    # A_diff_out using +/- 1.9cm to shroud and hub outlet radii

    print(f"Starting code...")

    diffuser1 = DiffuserCfg(
        A_diff_in=0.0153,
        A_diff_out=0.091, # Doing 4 circular combustion chambers, total of them = A_diff_out
        diff_eta_i=0.9
    )

    run_flag = 0
    recirc_factor = 3 # Recirculation factor to get effective volume, est for now
    

    if run_flag == 0:
        # Single run
        combustor1 = CombustorCfg(
            fuel_comp="C3H8:1",
            PR_b=0.95,
            n_b=0.98,
            primary_equivRatio=0.5,
            volume_b=0.0207*recirc_factor,
            f_primary=0.3,
            v_frac_primary=0.6
        )
        eng1 = Engine(T_t3=345.68, P_t3=130640, m_dot_air=1.388, diffuser=diffuser1, combustor=combustor1)
        comb_primary_gas_out, comb_secondary_gas_out = comb.combustor_main(eng1)

        T_prim_out = comb_primary_gas_out.T
        P_prim_out = comb_primary_gas_out.P
        X = comb_primary_gas_out.X
        fuel_prim_out = X[comb_primary_gas_out.species_index('C3H8')] #X[iCO2]:.6e

        T_secondary_out = comb_secondary_gas_out.T
        P_secondary_out = comb_secondary_gas_out.P
        X2 = comb_secondary_gas_out.X
        fuel_secondary_out = X2[comb_secondary_gas_out.species_index('C3H8')] #X[iCO2]:.6e

        print(f"Primary: T_out = {T_prim_out}, P_out = {P_prim_out}, fuel_out = {fuel_prim_out}")
        print(f"Secondary: T_out = {T_secondary_out}, P_out = {P_secondary_out}, fuel_out = {fuel_secondary_out}")






    if run_flag == 1:
        # Create input arrays
        filename = 'run_1-23-26n25-40'
        n = 25 # 10fraction increments
        n2 = 40 # 11volume increments
        f_primary_array = np.linspace(0.05, 0.95, n)
        v_frac_primary_array = np.linspace(0.05, 0.95, n)
        volume_b_array = np.linspace(0.001, 0.08, n2)
        
        # Create output arrays
        T_primary_out = np.full((n, n, n2), np.nan)
        P_primary_out = np.full((n, n, n2), np.nan)
        fuel_primary_out = np.full((n, n, n2), np.nan)
        O2_primary_out = np.full((n, n, n2), np.nan)
        converged = np.zeros((n, n, n2), dtype=bool)

        T_secondary_out = np.full((n, n, n2), np.nan)
        P_secondary_out = np.full((n, n, n2), np.nan)
        fuel_secondary_out = np.full((n, n, n2), np.nan)
        O2_secondary_out = np.full((n, n, n2), np.nan)

        print(f"Starting loops...")
        for i, f_primary in enumerate(f_primary_array):
            for j, v_frac_primary in enumerate(v_frac_primary_array):
                for k, volume_b in enumerate(volume_b_array):
                    if i % 10 == 0 and j == 0 and k == 0:
                        print(f"Running i={i}, j = {j}")
                    combustor1 = CombustorCfg(
                        fuel_comp="C3H8:1",
                        PR_b=0.95,
                        n_b=0.98,
                        primary_equivRatio=0.5,
                        volume_b=volume_b*recirc_factor,
                        f_primary=f_primary,
                        v_frac_primary=v_frac_primary
                    )

                    eng1 = Engine(T_t3=345.68, P_t3=130640, m_dot_air=1.388, diffuser=diffuser1, combustor=combustor1)
                    comb_primary_gas_out, comb_secondary_gas_out = comb.combustor_main(eng1)

                    T_primary_out[i, j, k] = comb_primary_gas_out.T
                    P_primary_out[i, j, k] = comb_primary_gas_out.P
                    X = comb_primary_gas_out.X
                    fuel_primary_out[i, j, k] = X[comb_primary_gas_out.species_index('C3H8')] #X[iCO2]:.6e
                    O2_primary_out[i, j, k] = X[comb_primary_gas_out.species_index('O2')]
                    converged[i, j, k] = True

                    T_secondary_out[i, j, k] = comb_secondary_gas_out.T
                    P_secondary_out[i, j, k] = comb_secondary_gas_out.P
                    X2 = comb_secondary_gas_out.X
                    fuel_secondary_out[i, j, k] = X2[comb_secondary_gas_out.species_index('C3H8')] #X[iCO2]:.6e
                    O2_primary_out[i, j, k] = X[comb_primary_gas_out.species_index('O2')]


        # Save data using pickle_util

        save(filename, 'T_primary_out', 'P_primary_out', 'fuel_primary_out', 'O2_primary_out', 'converged',
             'T_secondary_out', 'P_secondary_out', 'fuel_secondary_out', 'O2_primary_out',
             'f_primary_array', 'v_frac_primary_array', 'volume_b_array'
             )

        # Plot vol_primary and f_primary vs ignition(temp and fuel_X)
        #plot_vol_f(f_primary_array, v_frac_primary_array, T_out, fuel_out)
        """
        save figure 1 before closing, once closed figure 2 will show
        """


    if run_flag == 3:
        # Load data
        load_filename = 'run_1-23-26n25-40'
        load(load_filename)

        n = 25 # 10fraction increments
        n2 = 40 # 11volume increments
        f_primary_array = np.linspace(0.05, 0.95, n)
        v_frac_primary_array = np.linspace(0.05, 0.95, n)
        volume_b_array = np.linspace(0.001, 0.08, n2)

        plot_3D_scatter(f_primary_array, v_frac_primary_array, volume_b_array, T_primary_out, fuel_primary_out, T_ignite=1000.0, fuel_max=1e-3)
        plot_min_ignition_layer(0.0207, f_primary_array, v_frac_primary_array, volume_b_array, T_primary_out, fuel_primary_out, T_ignite=1000.0, fuel_max=1e-3, title=None)

        # Plot vol_primary and f_primary vs ignition(temp and fuel_X)
        #plot_vol_f(f_primary_array, v_frac_primary_array, T_out, fuel_out)
        """
        save figure 1 before closing, once closed figure 2 will show
        """

