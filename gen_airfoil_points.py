import numpy as np
import csv

# ---------------- Config ----------------
# Definicion de geometría tipo NACA
c = 0.30       # cuerda (m)
m = 0.06       # camber máximo (fracción de c)
p = 0.40       # posición del camber máximo (fracción de c)
t_rel = 0.12   # espesor relativo (fracción de c)
sharp_TE = False # True: TE cerrado (-0.1036), False: clásico (-0.1015)
N = 500      # puntos (max recomendado = 400)

# Rotación y spar
alpha = 3.0              # ángulo de incidencia (grados)
pivot = (0.25*c, 0.0)    # pivote rotación (quarter-chord)
x_spar_rot = 0.18        # posición del spar en el sistema ROTADO (m)

# Salida
out_csv = "airfoils_csv/naca6412.csv"

# --------- Fórmulas NACA 4 dígitos ----------
def yt(u, c, t_rel, sharp_TE=False):
    k5 = -0.1036 if sharp_TE else -0.1015
    return 5*t_rel*c*(0.2969*np.sqrt(u) - 0.1260*u - 0.3516*u**2 + 0.2843*u**3 + k5*u**4)

def yc(u, c, m, p):
    a = (m/p**2)*(2*p*u - u**2)
    b = (m/(1-p)**2)*((1-2*p) + 2*p*u - u**2)
    return c*np.where(u < p, a, b)

def dycdx(u, m, p):
    a = (2*m/p**2)*(p - u)
    b = (2*m/(1-p)**2)*(p - u)
    return np.where(u < p, a, b)

def naca4_upper_lower(c, m, p, t_rel, N=400, sharp_TE=False):
    u  = np.linspace(0.0, 1.0, N)
    x_c = u * c
    y_t = yt(u, c, t_rel, sharp_TE)
    y_c = yc(u, c, m, p)
    th  = np.arctan(dycdx(u, m, p))
    x_u = x_c - y_t*np.sin(th)
    y_u = y_c + y_t*np.cos(th)
    x_l = x_c + y_t*np.sin(th)
    y_l = y_c - y_t*np.cos(th)
    return x_u, y_u, x_l, y_l

def rotate_xy(x, y, alpha_deg, x0=0.0, y0=0.0):
    """Rota arrays x,y un ángulo alpha_deg (°) alrededor de (x0,y0). Convención: +CCW."""
    a = np.deg2rad(-alpha_deg)  # usa signo - si tuviste esa convención antes
    ca, sa = np.cos(a), np.sin(a)
    xr = x - x0; yr = y - y0
    x_rot = x0 + ca*xr - sa*yr
    y_rot = y0 + sa*xr + ca*yr
    return x_rot, y_rot

# --- helpers de interpolación y recorte en x ---
def _interp_on_curve(xq, x_curve, y_curve):
    idx = np.argsort(x_curve)
    x_sorted = x_curve[idx]; y_sorted = y_curve[idx]
    x_unique, keep_idx = np.unique(x_sorted, return_index=True)
    y_unique = y_sorted[keep_idx]
    if xq < x_unique[0] or xq > x_unique[-1]:
        raise ValueError(f"x={xq:.6f} fuera de rango [{x_unique[0]:.6f}, {x_unique[-1]:.6f}]")
    return np.interp(xq, x_unique, y_unique)

def clip_curve_at_x(x_curve, y_curve, x_cut, side="left"):
    y_cut = _interp_on_curve(x_cut, x_curve, y_curve)
    x_aug = np.concatenate([x_curve, [x_cut]])
    y_aug = np.concatenate([y_curve, [y_cut]])
    idx = np.argsort(x_aug)
    x_aug, y_aug = x_aug[idx], y_aug[idx]
    if side == "left":
        mask = x_aug <= x_cut + 1e-12
    else:
        mask = x_aug >= x_cut - 1e-12
    return x_aug[mask], y_aug[mask]

def cumulative_s(x, y):
    dx = np.diff(x); dy = np.diff(y)
    ds = np.sqrt(dx*dx + dy*dy)
    return np.concatenate(([0.0], np.cumsum(ds)))

# ---------------- Pipeline ----------------
# 1) Curvas exactas sin rotar
x_u, y_u, x_l, y_l = naca4_upper_lower(c, m, p, t_rel, N=N, sharp_TE=sharp_TE)

# 2) Rotar
pivot = tuple(pivot)  # por si viene como numpy
x_u_r, y_u_r = rotate_xy(x_u, y_u, alpha, *pivot)
x_l_r, y_l_r = rotate_xy(x_l, y_l, alpha, *pivot)

# 3) Recortar hasta el spar en el sistema rotado
x_u_left, y_u_left = clip_curve_at_x(x_u_r, y_u_r, x_spar_rot, side="left")  # TE/LE -> spar (asc)
x_l_left, y_l_left = clip_curve_at_x(x_l_r, y_l_r, x_spar_rot, side="left")  # TE/LE -> spar (asc)

# 4) Extremos del spar (sobre rotadas)
y_top = _interp_on_curve(x_spar_rot, x_u_r, y_u_r)
y_bot = _interp_on_curve(x_spar_rot, x_l_r, y_l_r)

# 5) Construir paneles con orientación CCW:
#    Upper: spar -> LE (invertir el tramo left)
x_upper = x_u_left[::-1]
y_upper = y_u_left[::-1]
s_upper = cumulative_s(x_upper, y_upper)
#    Lower: LE -> spar (tal cual left)
x_lower = x_l_left
y_lower = y_l_left
s_lower = cumulative_s(x_lower, y_lower)
#    Spar: bot -> top (vertical)
Nspar = 101
x_spar = np.full(Nspar, x_spar_rot)
y_spar = np.linspace(y_bot, y_top, Nspar)
s_spar = cumulative_s(x_spar, y_spar)

# 6) Exportar CSV
with open(out_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["panel", "index", "x", "y", "s"])  # s = longitud acumulada local
    for i, (xx, yy, ss) in enumerate(zip(x_upper, y_upper, s_upper)):
        w.writerow(["upper", i, f"{xx:.9g}", f"{yy:.9g}", f"{ss:.9g}"])
    for i, (xx, yy, ss) in enumerate(zip(x_lower, y_lower, s_lower)):
        w.writerow(["lower", i, f"{xx:.9g}", f"{yy:.9g}", f"{ss:.9g}"])
    for i, (xx, yy, ss) in enumerate(zip(x_spar, y_spar, s_spar)):
        w.writerow(["spar", i, f"{xx:.9g}", f"{yy:.9g}", f"{ss:.9g}"])

print(f"Puntos exportados a {out_csv}")