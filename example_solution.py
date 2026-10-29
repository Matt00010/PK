import matplotlib.pyplot as plt
import numpy as np

import pkmodel as pk

model = pk.Model(
    V_c = 10_000,
    CL = 1_000,
    V_p = [5_000, 5_000],
    Q_p = [1_000, 2_000]
)

boluses = [
        (0, 100_000),   # 100,000 ng at 0hr
        (12, 50_000)    # 50,000 ng at 12hr
    ]

infusions = [
        (5, 50, 10_000) # 10,000 ng/hr from 5h to 50h
    ]

protocol = pk.Protocol(
    boluses = boluses,
    infusions = infusions
)

solution = pk.Solution(model, protocol).solve(
    t_span=(0, 100),
    t_eval=np.linspace(0,100,1000)
)

fig, ax = plt.subplots()

for name in solution.model.compartment_names:
    solution.plot(name, ax=ax)

handles, labels = ax.get_legend_handles_labels()
unique_entries = dict(zip(labels, handles))
ax.legend(unique_entries.values(), unique_entries.keys())

ax.set_title("Drug Quantity Over Time - By Compartment", fontsize=14, pad=20)

# Draw the model and protocol (no simulation needed for this diagram)
diagram_ax = pk.diagram.plot_model_diagram(model, protocol)

plt.show()
