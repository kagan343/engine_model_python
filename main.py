
# Main engine scripts
from dataclasses import dataclass
import cantera as ct # global python is what installed cantera, 3.12.4
import combustor_main as comb



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
    equivRatio: float  
    volume_b: float  

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

    diffuser1 = DiffuserCfg(
        A_diff_in=0.0153,
        A_diff_out=0.0412,
        diff_eta_i=0.9
    )

    combustor1 = CombustorCfg(
        fuel_comp="C3H8:1",
        PR_b=0.95,
        n_b=0.98,
        equivRatio=0.3,
        volume_b=1, # test for code, 1m^3 gets ignition
    )

    eng1 = Engine(T_t3=345.68, P_t3=130640, m_dot_air=1.388, diffuser=diffuser1, combustor=combustor1)
    comb_gas_out = comb.combustor_main(eng1)
    
    # print(f"M_out = {M_out:.4f}, converged = {converged}") # testing print for now
    # print(f"P_out = {gas_out.P}, T_out = {gas_out.T}")


