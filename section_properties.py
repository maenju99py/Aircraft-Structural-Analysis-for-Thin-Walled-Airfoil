import pandas as pd
from pathlib import Path
import pandas as pd

# -------- parámetros --------
csv_path = Path("airfoils_points_files/naca6412.csv")
t = 1e-3  # espesor [m]

# -------- lectura CSV (convertir a objeto pandas) --------
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip().str.lower()
df = df.sort_values(["panel", "s"])

# -------- CSV de salida --------
out_dir = Path("geo_properties_files")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "naca6412_geo_props.csv"

# -------- hallamos la longitud de los paneles y los puntos medios --------
ds = df.groupby("panel")["s"].diff().fillna(0.0)
xm = 0.5*(df["x"] + df.groupby("panel")["x"].shift()).fillna(0.0)
ym = 0.5*(df["y"] + df.groupby("panel")["y"].shift()).fillna(0.0)

# -------- integrales de línea - propiedades de la seccion --------
# Calculo del area de linea
L_total = df.groupby("panel")["s"].max().sum()  # suma longitudes finales de cada panel
A = t * L_total

# Calculo de centroides
x_bar = t/A * (xm * ds).sum()
y_bar = t/A * (ym * ds).sum()

# Calculo de Inercias
Ixx = t * (ds * (ym - y_bar)**2).sum()
Iyy = t * (ds * (xm - x_bar)**2).sum()
Ixy = t * (ds * (xm - x_bar)*(ym - y_bar)).sum()

# -------- imprimir resultados --------
print("=== Thin-plate (midpoint rule) ===")
print(f"t = {t * 1e3 :.2f} mm")
print(f"Área thin-plate = {A * 1e6 :.2f} mm^2")
print(f"x̄ = {x_bar * 1e3 :.2f} mm")
print(f"ȳ = {y_bar * 1e3 :.2f} mm")
print(f"Ixx = {Ixx * 1e12 :.0f} mm^4")
print(f"Iyy = {Iyy * 1e12 :.0f} mm^4")
print(f"Ixy = {Ixy * 1e12 :.0f} mm^4")

# -------- guardar resultados en CSV (metros) --------
props = pd.DataFrame({
    "t": [t],
    "A":  [A],
    "xbar":[x_bar],
    "ybar":[y_bar],
    "Ixx":[Ixx],
    "Iyy":[Iyy],
    "Ixy":[Ixy],
})
props.to_csv(out_path, index=False)
print(f"Guardado en {out_path}")