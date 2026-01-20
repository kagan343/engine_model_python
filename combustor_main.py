
# Combustor main
from fnc_comb import iterate_diffuser
from fnc_comb import single_flow_combustion


def combustor_main(eng):

    # Set diffuser composition to air
    air_X = 'O2:0.21, N2:0.79'
    eng.diff_gas_in.X = air_X
    eng.diff_gas_out.X = air_X

    # Set diffuser temp and pressure to compressor outlet values (outlet guess same as inlet)
    eng.diff_gas_in.TP = eng.T_t3, eng.P_t3
    eng.diff_gas_out.TP = eng.T_t3, eng.P_t3

    # print(f'gas in comp = {eng.diff_gas_in.X}')
    # print(f'gas out comp = {eng.diff_gas_out.X}')
    # print(f'gas in temp and pressure = {eng.diff_gas_in.T} and {eng.diff_gas_in.P}')
    # print(f'gas out temp and pressure = {eng.diff_gas_out.T} and {eng.diff_gas_out.P}')

    ## Diffusor section
    # iterate to get diffuser outputs since mass, T, P, cp, cv, etc are implicit
    # current getting good results, velocity down to 25 m/s with +/- 1.9cm to shroud and hub radii
    # static pressure increases with decreased velocity
    # stagnation/ total pressure small decrease due to losses modelled by eta_i (diff efficiency)
    M_out, converged, diff_gas_out, diff_mdot_out = iterate_diffuser(eng)

    if converged:
        comb_gas_out = single_flow_combustion(eng, diff_gas_out, diff_mdot_out)
        print(comb_gas_out.T)
        print(comb_gas_out.P)

    return comb_gas_out # change

