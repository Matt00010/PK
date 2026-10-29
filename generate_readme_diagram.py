
"""Generate a representative IV and SC compartment diagram for the README."""

from pathlib import Path

import matplotlib.pyplot as plt

from pkmodel import Model, Protocol
from pkmodel.diagram import plot_model_diagram

# Both models use the same distribution and clearance parameters.
iv_model = Model(
    V_c=10_000,
    CL=1_000,
    V_p=[5_000, 3_000],
    Q_p=[1_000, 1_500],
)
sc_model = Model(
    V_c=10_000,
    CL=1_000,
    V_p=[5_000, 3_000],
    Q_p=[1_000, 1_500],
    k_a=0.8,
)

# Example protocols include both bolus dosing and constant-rate infusion.
iv_protocol = Protocol(
    boluses=[(0, 100_000), (24, 50_000)],
    infusions=[(8, 18, 7_000)],
)
sc_protocol = Protocol(
    boluses=[(0, 80_000), (24, 40_000)],
    infusions=[(8, 18, 5_000)],
)

# Match the panel widths to the diagram's horizontal coordinate ranges.
fig, axes = plt.subplots(
    1, 2,
    figsize=(19, 6.5),
    gridspec_kw={"width_ratios": [10, 13.05]},
)
plot_model_diagram(iv_model, iv_protocol, ax=axes[0])
plot_model_diagram(sc_model, sc_protocol, ax=axes[1])
fig.subplots_adjust(left=0.03, right=0.98, top=0.90, bottom=0.08, wspace=0.10)

output = Path("docs/images/pk_model_diagrams.png")
output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output, dpi=190, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved {output}")
