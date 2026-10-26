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
        assert "central" in m1.compartment_names
        assert m1.dose_compartment_index == 0

    def test_compartment_names(self, A1, m1):
        """
        Test compartment names
        """
        p = A1()
        if p["k_a"] is None:
            assert m1.compartment_names[0] == "central"
            assert "absorption" not in m1.compartment_names
            assert m1.n_compartments == len(p["Q_p"]) + 1
        else:
            assert m1.compartment_names[0] == "absorption"
            assert m1.compartment_names[1] == "central"
            assert m1.n_compartments == len(p["Q_p"]) + 2

    def test_rhs_not_implemented_yet(self, A1, m1):
        """
        Test that calling rhs on the model yields a NotImplementedError
        if the peripheral compartments were not provided
        """
        p = A1()
        if p["Q_p"] is None:
            with pytest.raises(NotImplementedError):
                assert m1.rhs(0.0, [0.0])


