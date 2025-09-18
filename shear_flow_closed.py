import pandas as pd
from pathlib import Path
from shear_flow_open import qs_basic
import numpy as np

if __name__ == "__main__":
    # -------- parámetros --------
    t = 1e-3    # espesor [m]
    Sx = 0      # cortante en X [N]
    Sy = 250    # cortante en Y [N]
    x_load = 116.2*1e-3 # coordenada de aplicacion de Sy [m]

    # --- leer propiedades geométricas centroidales (m, m^4) ---
    props_path = Path("geo_properties_files/naca6412_geo_props.csv")
    props = pd.read_csv(props_path)

    Ixx = float(props.at[0, "Ixx"])     # [m^4]
    Iyy = float(props.at[0, "Iyy"])     # [m^4]
    Ixy = float(props.at[0, "Ixy"])     # [m^4]
    xbar = float(props.at[0, "xbar"])     # [m]
    ybar = float(props.at[0, "ybar"])     # [m]

    print("Props cargadas:",
        f"Ixx={Ixx:.6e}, Iyy={Iyy:.6e}, Ixy={Ixy:.6e}, x̄={xbar:.6e}, ȳ={ybar:.6e}")

    # -------- lectura CSV de paneles --------
    seg_path = Path("panels_files/panels_naca6412.csv")
    seg = pd.read_csv(seg_path, index_col=0)

    # -------- calculo de flujo basico --------
    out = qs_basic(seg, t, Sx, Sy, Ixx, Iyy, Ixy, xbar, ybar)
    qb  = out["qs_b"].to_numpy() 

    # -------- calculo de q0 --------
    # 1) área encerrada por la línea media (shoelace sobre midpoints)
    x = seg["xm"].to_numpy()
    y = seg["ym"].to_numpy()
    A_cell = 0.5 * np.abs(np.sum(x*np.roll(y, -1) - np.roll(x, -1)*y))

    # 2) brazo p = r × t
    sin_th = np.sin(seg["theta"].to_numpy())
    cos_th = np.cos(seg["theta"].to_numpy())

    p   = x*sin_th - y*cos_th
    ds  = seg["ds"].to_numpy()
    T_b = np.sum(p * qb * ds)

    # 3) torque externo respecto al centroide y q0
    xi = x_load - xbar       # m
    T_ext = -Sy * xi            # N·m  (Sx=0)
    q0 = (T_ext - T_b) / (2.0 * A_cell)   # N/m

    # 4) flujo total y tensión
    out["q_total"] = out["qs_b"] + q0      # N/m
    out["tau"] = out["q_total"] / t    # Pa

    # -------- exportar a CSV --------
    out.to_csv("shear_files/seg_q_tau_naca6412.csv", index=True, float_format="%.6f")