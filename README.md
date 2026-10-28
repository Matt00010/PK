# Pharmokinetic Modelling Package (PKModel_marks)
PKModel_marks is a python package for solving and visualising pharmokinetic models.

## Package structure
```text
PK/
├── pkmodel/
│   ├── model.py
│   ├── protocol.py
│   ├── solution.py
│   ├── version_info.py
│   └── tests/
│       ├── test_model.py
│       ├── test_protocol.py
│       └── test_solution.py
├── README.md
├── pyproject.toml
├── app.py
└── LICENSE
```

| Script | Description |
|-------|-------------|
| `Model` | Defines the model parameters and calculates how drug quantity changes over time across each compartment. |
| `Protocol` | Defines whether the drug administration is continuous or instantaneous bolus. |
| `Solution` | 	Solves the PK model with SciPy and visualises the changes in drug quantity over time |

## Installing PKM

```python
python -m pip install PKModel_marks
```

## Requirements
```python
import numpy as np
import PKModel_marks as pk
import matplotlib.pyplot as plt
```

## Example

**1. Define the model**
For intravenous administration:
```python
model = pk.Model(
    V_c = 10_000,
    CL = 1_000,
    V_p = [5_000],
    Q_p = [1_000]
)
```

For subcutaneous administration, specify the k_a parameter.

**2. Define the dosing protocol**

```python
protocol = pk.Protocol(
    boluses = [
        (0, 100_000),   # 100,000 ng at 0hr
        (12, 50_000)    # 50,000 ng at 12hr
    ],
    infusions = [
        (2, 4, 10_000) # 10,000 ng/hr from 2h to 4h (i.e. over the period [2,4))
    ]
)
```

**3. Solve the model and visualise**
```python
solution = pk.Solution(model, protocol).solve(
    t_span=(0, 24),
    t_eval=np.linspace(0,24,1000)
)

print(solution.t)
print(solution.y[0])
solution.plot("central")
solution.plot("peripheral_1")

plt.show()
```

## Interactive Demonstration 
Install the optional Streamlit dependency and launch the comparison app from
the repository root:
```powershell
pip install -e ".[app]"
streamlit run app.py
```

## Contributors
Developed as part of the Software Engineering model in the Doctoral Training Centre (DTC).
* Matt
* Adam
* Reefe
* Katie
* Saja
