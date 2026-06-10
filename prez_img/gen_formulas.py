"""Renderuje wzory matematyczne do PNG (przezroczyste tło) na slajdy."""

import os

import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = "#1E2761"
WHITE = "#FFFFFF"

FORMULAS = {
    "f_cel": (r"$\min_{x,\,\beta,\,z}\ \ \beta\ +\ \frac{1}{1-\alpha}"
              r"\sum_{j=1}^{m} p_j\, z_j$", 26, NAVY),
    "f_ogr1": (r"$z_j \,\geq\, x^{\top}(S_0 - s_j) - \beta,"
               r"\qquad z_j \,\geq\, 0$", 20, NAVY),
    "f_ogr2": (r"$x^{\top} S_0 \,=\, V_0$", 20, NAVY),
    "f_ogr3": (r"$\frac{1}{V_0}\sum_{j=1}^{m} p_j\, x^{\top}(s_j - S_0)"
               r" \,=\, r_e$", 20, NAVY),
    "f_ogr4": (r"$x \,\geq\, 0$", 20, NAVY),
    "f_cvar": (r"$\mathrm{CVaR}_{\alpha}(x) \,=\, "
               r"E\left(L_T(x)\ \mid\ L_T(x) > \mathrm{VaR}_{\alpha}(x)\right)$",
               22, NAVY),
    "f_cena": (r"$S_{t+1} \,=\, S_t\,\left(1 + \mu(\mathrm{stan}) + "
               r"\sigma(\mathrm{stan})\cdot Z\right),\quad Z\sim N(0,1)$",
               20, NAVY),
    "f_strata": (r"$L_T(x) \,=\, -\left(V_T(x) - V_0\right)$", 20, NAVY),
}


def render(name, tex, fontsize, color):
    fig = plt.figure(figsize=(0.1, 0.1))
    txt = fig.text(0, 0, tex, fontsize=fontsize, color=color)
    fig.canvas.draw()
    bbox = txt.get_window_extent()
    fig.set_size_inches(bbox.width / fig.dpi + 0.1, bbox.height / fig.dpi + 0.1)
    fig.savefig(os.path.join(OUT, f"{name}.png"), dpi=300, transparent=True,
                bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


if __name__ == "__main__":
    for name, (tex, fs, col) in FORMULAS.items():
        render(name, tex, fs, col)
    print("OK")
