import numpy as np
import pkmodel as pk
import matplotlib.pyplot as plt

model = pk.Model(
    V_c = 10_000,
    CL = 1_000,
    V_p = [5_000],
    Q_p = [1_000]
)

protocol = pk.Protocol(
    boluses = [
        (0, 100_000),   # 100,000 ng at 0hr
        (12, 50_000)    # 50,000 ng at 12hr
    ],
    infusions = [
        (2, 4, 10_000) # 10,000 ng/hr from 2h to 4h (i.e. over the period [2,4))
    ]
)

solution = pk.Solution(model, protocol).solve(
    t_span=(0, 24),
    t_eval=np.linspace(0,24,1000)
)

print(solution.t)
print(solution.y[0])
solution.plot("central")
solution.plot("peripheral_1")

plt.show()