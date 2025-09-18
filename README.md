# Aircraft Structural Analysis (Thin-Walled, NACA Airfoils)

Tools to compute basic shear flow ($q_b$), the closed-section constant ($q_0$), total shear flow ($q$), and shear stress ($\tau$) around an airfoil modeled as a thin-walled single cell. Line integrals are done with the midpoint rule; closed-section behavior follows Bredt–Batho.

<img width="1079" height="316" alt="image" src="https://github.com/user-attachments/assets/982e6155-f7e9-4f70-9afe-981773bc15a0" />

## What this project does

1) Builds panel segments along the airfoil midline: $x_m$, $y_m$, $ds$, $\theta_{ds}$].

2) Computes thin-plate geometric properties: area, centroid ($\bar{x}$, $\bar{y}$), and centroidal inertias ($I_{xx}$, $I_{yy}$, $I_{xy}$).

3) Computes basic shear flow $q_b(s)$ for given shear resultants ($S_x$, $S_y$).

4) Solves the closed-section constant $q_0$ either by:
   
    a) Compatibility (load through the shear center ⇒ zero twist),
   
    b) or Moment equilibrium using a known load application point ($x_{load}$, $y_{load}$).

7) Exports CSVs and plots $q$ or $\tau$ around the contour.

## Quick Start

#### 1) Generate airfoil points
Run gen_airfoil_points.py. In this script you specify the NACA code, chord, angle of incidence, number of control points, and (optionally) a trailing-edge cut.
Output: a CSV in airfoils_points_files/.

#### 2) Quick visual check
Run plot_airfoil.py to visualize the generated profile and confirm everything looks right.

#### 3) Build panels for line integrals
Run gen_panels.py to create the midline segments (xm, ym, ds[, theta]) in CCW order.
Output: a CSV in panels_files/.

#### 4) Compute section properties (thin-plate)
Run section_properties.py to compute area, centroid (xbar, ybar), and centroidal inertias (Ixx, Iyy, Ixy) in SI units.
Output: a CSV in geo_properties_files/.

#### 5) Shear flow for the closed section
Run shear_flow_closed.py. Set the wall thickness t, the shear resultants Sx, Sy, and (if needed) the load application coordinates. The script computes basic flow q_b, solves q0, and returns total shear flow q and shear stress tau.
Output: CSV in shear_files/.

#### 6) Plot the distribution
Run plot_shear_distribution.py to plot q or tau along the contour and versus arc-length s.

<img width="988" height="374" alt="image" src="https://github.com/user-attachments/assets/f75a58e4-2d8e-4b6f-b561-10a1f6d0d12b" />

<img width="970" height="422" alt="image" src="https://github.com/user-attachments/assets/8ee68efb-5acb-4911-93ac-3888b1be954f" />


## Based On

#### 1) Airfoil geometry (NACA 4-digit)
Standard analytic construction of mean camber and thickness distributions for NACA 4-digit sections, following common references (e.g., Abbott & von Doenhoff). For a quick primer we originally consulted this tutorial:
https://towardsdatascience.com/introduction-to-naca-airfoil-aerodynamics-in-python-72a1c3ee46b1/

#### 2) Line integrals (discretization)
Numerical line integrals are approximated with the midpoint rule over straight segments (panels):
https://math.libretexts.org/Courses/Mount_Royal_University/Calculus_for_Scientists_II/2%3A_Techniques_of_Integration/2.5%3A_Numerical_Integration_-_Midpoint%2C_Trapezoid%2C_Simpson's_rule

#### 3) Shear flow in thin-walled closed sections
Formulation follows Bredt–Batho and the open/closed section development in Aircraft Structures for Engineering Students (T.H.G. Megson).

$$q_s = -(\frac{S_xI_{xx}-S_yI_{xy}}{I_{xx}I_{yy}-I_{xy}^2}) \int_{0}^{s} txds -(\frac{S_yI_{yy}-S_xI_{xy}}{I_{xx}I_{yy}-I_{xy}^2}) \int_{0}^{s} tyds + q_{s,0} $$

## Limitations

1) Thin-walled single cell only.

2) No multi-cell coupling (can be extended).

3) Geometry and properties must use the same reference frame.

## Credits

Author: maenju (https://github.com/maenju99py)

email: maenju99@gmail.com  

LinkedIn: https://www.linkedin.com/in/marcelo-enciso-904443235/
