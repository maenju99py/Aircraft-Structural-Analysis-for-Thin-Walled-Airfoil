import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---- paths ----
seg_path = Path("shear_files/seg_q_tau_naca6412.csv")  # debe tener: panel,xm,ym,ds, q_total, tau

# ---- qué variable graficar: "q_total" (N/m) o "tau" (Pa) ----
var_name = "tau"   # cambia a "tau" si querés tensiones

# ---- leer y limpiar ----
df = pd.read_csv(seg_path)
# quitar columnas índice si quedaron guardadas
df = df.loc[:, ~df.columns.str.contains(r"^Unnamed", case=False)]
# normalizar headers
df.columns = df.columns.str.strip().str.lower()

# checks mínimos
req = {"panel", "xm", "ym", "ds", var_name}
missing = req - set(df.columns)
if missing:
    raise ValueError(f"Faltan columnas {missing} en {seg_path}")

# ---- s acumulado (longitud a lo largo del contorno) ----
df["s"] = df["ds"].cumsum()               # [m]
df["s_mm"] = df["s"] * 1e3                # [mm]

# ---- figuras ----
fig = plt.figure(figsize=(10, 8))

# (A) Perfil en XY coloreado por var
ax1 = plt.subplot(2, 1, 1)
# una línea tenue para ver el contorno
for p, g in df.groupby("panel", sort=False):
    ax1.plot(g["xm"], g["ym"], lw=1, alpha=0.4, label=p)

sc = ax1.scatter(df["xm"], df["ym"], c=df[var_name], s=18)
cb = plt.colorbar(sc, ax=ax1, fraction=0.046, pad=0.04)
cb.set_label(f"{var_name} [{'N/m' if var_name=='q_total' else 'Pa'}]")

ax1.set_aspect("equal", adjustable="box")
ax1.set_xlabel("x [m]")
ax1.set_ylabel("y [m]")
ax1.set_title(f"Airfoil colored by {var_name}")
ax1.legend(loc="best", fontsize=8)

# (B) Distribución vs s
ax2 = plt.subplot(2, 1, 2, sharex=None)
ax2.plot(df["s_mm"], df[var_name], lw=1.8)
ax2.set_xlabel("s [mm]")
ax2.set_ylabel(f"{var_name} [{'N/m' if var_name=='q_total' else 'Pa'}]")
ax2.grid(True, alpha=0.3)
ax2.set_title(f"{var_name} along contour")

plt.tight_layout()
plt.show()