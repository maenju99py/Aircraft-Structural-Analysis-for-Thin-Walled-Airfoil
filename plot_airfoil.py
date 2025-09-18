import csv
import numpy as np
import matplotlib.pyplot as plt

in_csv = "airfoils_csv/naca6412.csv"  # mismo nombre del script generador

# Leer CSV
panels = {"upper": [], "lower": [], "spar": []}
with open(in_csv, "r", newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        panels[row["panel"]].append((float(row["x"]), float(row["y"]), float(row["s"])))

# Ordenar por índice de arc-length s dentro de cada panel
for k in panels:
    panels[k] = np.array(sorted(panels[k], key=lambda t: t[2]))  # (x,y,s)

# Extraer arrays
xu, yu = panels["upper"][:,0], panels["upper"][:,1]
xl, yl = panels["lower"][:,0], panels["lower"][:,1]
xs, ys = panels["spar"][:,0],  panels["spar"][:,1]

# Plot
plt.figure(figsize=(7,3))
plt.plot(xu, yu, lw=1.8, label="Upper (spar→LE)")
plt.plot(xl, yl, lw=1.8, label="Lower (LE→spar)")
plt.plot(xs, ys, lw=2.0, label="Spar (bot→top)")
plt.gca().set_aspect("equal", adjustable="box")
plt.grid(True, alpha=0.3)
plt.xlabel("x' [m]"); plt.ylabel("y' [m]")
plt.title("Airfoil rotado — paneles exportados")
plt.legend(); plt.tight_layout(); plt.show()