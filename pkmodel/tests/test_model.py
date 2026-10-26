import unittest
import pytest

import pkmodel as pk

@pytest.fixture(scope="session")
def A1():
    return {
        "name": "model1",
        "Q_p": 1,
        "V_c": 1,
        "V_p": 1,
        "CL": 1,
        "k_a": 1
    }

@pytest.fixture(scope="session")
def m1(A1):
    params = A1()
    return pk.Model(
        params["name"],
        params["Q_p"],
        params["V_c"],
        params["V_p"],
        params["CL"],
        params["k_a"]
        )

class TestModel():
    """
    Tests the :class:`Model` class.
    """
    def test_create_model(self, A1, m1):
        """
        Tests Model creation.
        """
        p = A1()
        assert m1.name == p["name"]
        assert m1.Q_p1 == p["Q_p"]
        assert m1.V_c == p["V_c"]
        assert m1.V_p1 == p["V_p"]
        assert m1.CL == p["CL"]
        assert m1.k_a == p["k_a"]
        assert m1.n_components == len(p["Q_p"])
        assert m1.dose_compartment_index == 0

