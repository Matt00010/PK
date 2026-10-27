import numpy as np
import pkmodel as pk
import matplotlib.pyplot as plt

model = pk.Model(
    V_c = 10_000,
    CL = 1_000,
    V_p = [5_000],
    Q_p = [1_000]
)

boluses = [
        (0, 100_000),   # 100,000 ng at 0hr
        (12, 50_000)    # 50,000 ng at 12hr
    ]

infusions = [
        (5, 50, 10_000) # 10,000 ng/hr from 5h to 25h
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
    solution.plot(protocol, name, ax=ax)

plt.legend()
plt.show()