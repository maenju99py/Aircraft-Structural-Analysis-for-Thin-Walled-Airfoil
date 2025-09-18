import pandas as pd
from pathlib import Path
import numpy as np

csv_path = Path("airfoil_points_files/naca6412.csv")
out_path = Path("panels_files/panels_naca6412.csv")

# leer y ordenar (upper→lower→spar; s creciente dentro de cada panel)
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip().str.lower()
df["panel"] = pd.Categorical(df["panel"], ["upper","lower","spar"], ordered=True)
df = df.sort_values(["panel", "s"]).reset_index(drop=True)

# Δs y puntos medios (midpoint rule) por panel
df["ds"] = df.groupby("panel", observed=True)["s"].diff().fillna(0.0)
df["dx"] = df.groupby("panel", observed=True)["x"].diff()
df["dy"] = df.groupby("panel", observed=True)["y"].diff()
df["theta"] = np.arctan2(df["dy"], df["dx"])  # ángulo del segmento (rad)
df["xm"] = 0.5 * (df["x"] + df.groupby("panel", observed=True)["x"].shift()).fillna(0.0)
df["ym"] = 0.5 * (df["y"] + df.groupby("panel", observed=True)["y"].shift()).fillna(0.0)

# DB de paneles
seg = df.loc[df["ds"] > 0, ["panel", "xm", "ym", "ds", "theta"]].copy()

# guardar a csv
out_path.parent.mkdir(parents=True, exist_ok=True)
seg.to_csv(out_path, index=True)
print(f"OK: {len(seg)} segmentos guardados en {out_path}")