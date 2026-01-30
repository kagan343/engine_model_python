# Plotting functions
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


def plot_min_ignition_layer(volume_point, f_array, v_frac_array, volume_b_array, T_out, fuel_out,
                            T_ignite=1000.0, fuel_max=1e-3, title=None):
    """
    Finds the lowest volume_b layer that has ANY ignition points, then:
    """
    n = len(f_array)
    nv = len(v_frac_array)
    n2 = len(volume_b_array)

    if T_out.shape != (n, nv, n2) or fuel_out.shape != (n, nv, n2):
        raise ValueError(
            f"Expected T_out and fuel_out shape {(n, nv, n2)}; "
            f"got T_out {T_out.shape}, fuel_out {fuel_out.shape}."
        )

    valid = np.isfinite(T_out) & np.isfinite(fuel_out)
    ign_mask = valid & (T_out >= T_ignite) & (fuel_out <= fuel_max)

    # --- Select layer k_sel ---
    k_sel = None

    if isinstance(volume_point, str) and volume_point.strip().lower() == "min":
        for k in range(n2):
            if np.any(ign_mask[:, :, k]):
                k_sel = k
                break

        if k_sel is None:
            print("No ignition found on any volume_b layer.")
            return None, None, None

    else:
        vol_target = float(volume_point)
        k_sel = int(np.argmin(np.abs(volume_b_array - vol_target)))

    volume_sel = float(volume_b_array[k_sel])
    layer_mask = ign_mask[:, :, k_sel]

    if not np.any(layer_mask):
        print(f"No ignition points on selected layer: k={k_sel}, volume_b={volume_sel:g}")
        return k_sel, volume_sel, None

    # Indices of ignited points on that layer
    ij = np.argwhere(layer_mask)  # rows: [i, j]
    i_idx = ij[:, 0]
    j_idx = ij[:, 1]

    f_pts = f_array[i_idx]
    v_pts = v_frac_array[j_idx]

    # --- Min f that ignites, and a corresponding v ---
    min_f_val = float(np.min(f_pts))
    min_f_candidates = ij[f_pts == min_f_val]
    j_at_min_f = int(np.min(min_f_candidates[:, 1]))
    v_at_min_f = float(v_frac_array[j_at_min_f])

    # --- Min v that ignites, and a corresponding f ---
    min_v_val = float(np.min(v_pts))
    min_v_candidates = ij[v_pts == min_v_val]
    i_at_min_v = int(np.min(min_v_candidates[:, 0]))
    f_at_min_v = float(f_array[i_at_min_v])

    # Plot only that layer (2D)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(f_pts, v_pts, s=25, alpha=0.8, edgecolors="black", linewidths=0.3)

    # Highlight the two “extreme” points we reported
    ax.scatter([min_f_val], [v_at_min_f], s=80, edgecolors="black", linewidths=0.8)
    ax.scatter([f_at_min_v], [min_v_val], s=80, edgecolors="black", linewidths=0.8)

    ax.set_xlabel("f_primary")
    ax.set_ylabel("v_frac_primary")

    if title is None:
        if isinstance(volume_point, str) and volume_point.strip().lower() == "min":
            title = f"Lowest Ignition Layer: volume_b = {volume_sel:g} (k={k_sel})"
        else:
            title = f"Selected Layer (closest to {float(volume_point):g}): volume_b = {volume_sel:g} (k={k_sel})"
    ax.set_title(title)

    ax.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.show()

    result = {
        "k_sel": k_sel,
        "volume_b_sel": volume_sel,
        "volume_point_input": volume_point,
        "min_f_primary": min_f_val,
        "v_frac_at_min_f": v_at_min_f,
        "min_v_frac_primary": min_v_val,
        "f_primary_at_min_v": f_at_min_v,
        "n_ignited_points_on_layer": int(ij.shape[0]),
    }

    print(f"Selected layer: k={k_sel}, volume_b={volume_sel:g}")
    print(f"Min f_primary on that layer: {min_f_val:g} at v_frac_primary={v_at_min_f:g}")
    print(f"Min v_frac_primary on that layer: {min_v_val:g} at f_primary={f_at_min_v:g}")
    print(f"Ignited points on layer: {result['n_ignited_points_on_layer']}")


def plot_3D_scatter(f_array, v_frac_array, volume_b_array, T_out, fuel_out, T_ignite=1000.0, fuel_max=1e-3):
    """
    Plot vol_primary,f_primary,volume_b_array as 3d scatter, each point is checked with its corresponding
    T_out and fuel_out, is temp and fuel percent meet ignition criteria then point is plotted
    """
    ### Plots ### (from chat way quicker than looking up plotting documentation)    
    F, V, VB = np.meshgrid(f_array, v_frac_array, volume_b_array, indexing="ij")

    valid = np.isfinite(T_out) & np.isfinite(fuel_out) # Exclude NaN/inf
    ign_mask = valid & (T_out >= T_ignite) & (fuel_out <= fuel_max) # Ignition criteria

    # Flatten for scatter plotting
    Fx = F.ravel()
    Vy = V.ravel()
    Vbz = VB.ravel()
    ign_flat = ign_mask.ravel()
    valid_flat = valid.ravel()

    # Create plot
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    
    sc = ax.scatter(
            Fx[ign_flat], Vy[ign_flat], Vbz[ign_flat],
            c=Vbz[ign_flat],
            cmap="viridis",
            s=18, marker="o",
            alpha=0.8,
            edgecolors="black",
            linewidths=0.3
        )

    cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1)
    cbar.set_label("volume_b")
    
    # Axis and title
    ax.set_xlabel("f_primary")
    ax.set_ylabel("v_frac_primary")
    ax.set_zlabel("volume_b")
    title = f"3D Ignition Scatter (T >= {T_ignite:g} K, fuel <= {fuel_max:g})"
    ax.set_title(title)

    plt.tight_layout()
    plt.show()

    # Print amount of points
    n_valid = int(np.sum(valid))
    n_ign = int(np.sum(ign_mask))
    print(f"Valid points: {n_valid}")
    print(f"Ignited points: {n_ign}")


def plot_vol_f(f_primary_array, v_frac_primary_array, T_out, fuel_out):
    """
    Plot vol_primary and f_primary vs ignition(temp and fuel_X)
    """
    ### Plots ### (from chat way quicker than looking up plotting documentation)
    # 3d plot
    F, V = np.meshgrid(f_primary_array, v_frac_primary_array, indexing='ij')
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    T_masked = np.ma.masked_invalid(T_out)
    surf = ax.plot_surface(F, V, T_masked, cmap='inferno', edgecolor='none')
    ax.set_xlabel('f_primary')
    ax.set_ylabel('v_frac_primary')
    ax.set_zlabel('T_out [K]')
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Temperature [K]')
    plt.tight_layout()
    plt.show()
    # 2D contour
    burned = (T_out > 1000) & (fuel_out < 1e-3)
    plt.figure(figsize=(6,5))
    plt.contourf(F, V, burned, levels=[-0.5, 0.5, 1.5], colors=['blue','red'])
    plt.xlabel('f_primary')
    plt.ylabel('v_frac_primary')
    plt.title('Ignition Envelope (orange = burning)')
    plt.show()