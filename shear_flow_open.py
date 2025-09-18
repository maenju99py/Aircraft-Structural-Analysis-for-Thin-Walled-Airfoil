import pandas as pd
from pathlib import Path

def qs_basic(seg: pd.DataFrame, t, Sx, Sy, Ixx, Iyy, Ixy, xbar, ybar) -> pd.DataFrame:
    """
    Devuelve una copia de 'seg' con columnas Qy, Qx y qs_b (shear flow básico, sin q0).
    Requiere columnas: panel, xm, ym, ds (en metros).
    """
    s = seg.copy()

    # acumulados de primeros momentos (midpoint rule)
    s["Qy"] = (t * (s["xm"] - xbar) * s["ds"]).cumsum()  # ≈ ∫ t·x ds
    s["Qx"] = (t * (s["ym"] - ybar) * s["ds"]).cumsum()  # ≈ ∫ t·y ds

    # constantes de la fórmula
    D = Ixx * Iyy - Ixy**2
    Aconst = -(Sx * Ixx - Sy * Ixy) / D
    Bconst = -(Sy * Iyy - Sx * Ixy) / D

    # q_b(s) = -(A·Qy + B·Qx)
    s["qs_b"] = -(Aconst * s["Qy"] + Bconst * s["Qx"])
    return s


if __name__ == "__main__":
      # -------- parámetros --------
      csv_path = Path("airfoils_csv/naca6412.csv")
      t = 1e-3  # espesor [m]
      Sx = 0      # cortante en X [N]
      Sy = 250    # cortante en Y [N]

      # --- leer propiedades geométricas centroidales (m, m^4) ---
      props_path = Path("geo_properties_files/naca6412_geo_props.csv")
      props = pd.read_csv(props_path)

      Ixx   = float(props.at[0, "Ixx"])     # [m^4]
      Iyy   = float(props.at[0, "Iyy"])     # [m^4]
      Ixy   = float(props.at[0, "Ixy"])     # [m^4]
      xbar = float(props.at[0, "xbar"])   # [m]
      ybar = float(props.at[0, "ybar"])   # [m]

      print("Props cargadas:",
            f"Ixx={Ixx:.6e}, Iyy={Iyy:.6e}, Ixy={Ixy:.6e}, x̄={xbar:.6e}, ȳ={ybar:.6e}")

      # -------- lectura CSV de paneles --------
      seg_path = Path("panels_files/panels_naca6412.csv")
      seg = pd.read_csv(seg_path, index_col=0)

      # -------- calculo de flujo basico --------
      out = qs_basic(seg, t, Sx, Sy, Ixx, Iyy, Ixy, xbar, ybar)

      # ---- guarda los resultados a csv ----
      out_dir = Path("shear_files")
      out_dir.mkdir(parents=True, exist_ok=True)
      out_path = out_dir / "qb_naca6412.csv"
      out.to_csv(out_path, index=True)
      print(f"OK: resultados guardados en {out_path}")