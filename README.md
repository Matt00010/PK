# Pharmokinetic Modelling Package (PKM)
PKM is a python package for solving and visualising pharmokinetic models. 

## Package structure
PK/
├── pkmodel/
│   ├── model.py
│   ├── protocol.py
│   ├── solution.py
│   ├── version_info.py
│   ├── tests/
│   │   ├── test_model.py
│   │   ├── test_protocol.py
│   │   └── test_solution.py
├── README.md
├── pyproject.toml
├── app.py
└── LICENSE

| Class | Description |
|-------|-------------|
| `Model` | X |
| `Protocol` | X |
| `Solution` | X |

## Requirements
* NumPy
* SciPy
* Matplotlib

## Installing PKM

```python
git clone https://github.com/USERNAME/PK.git
cd PK
python -m pip install -e
```

## Contributors
Developed as part of the Software Engineering model in the Doctoral Training Centre (DTC).
* Adam
* Matt
* Saja
* Reefe
* Katie
# 2026 Software Engneering

Starter PK modelling repository.

## Interactive demonstration

Install the optional Streamlit dependency and launch the comparison app from
the repository root:

```powershell
pip install -e ".[app]"
streamlit run app.py
```

The app compares two model parameter sets under the same infusion protocol.
It is an educational demonstration, not a clinical decision-making tool.
