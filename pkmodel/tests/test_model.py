import numpy.testing as npt
import pytest

import pkmodel as pk


@pytest.fixture(
    scope="session",
    params=[
        {
            "Q_p": [1],
            "V_c": 1,
            "V_p": [1],
            "CL": 1,
            "k_a": None,
        },
        {
            "Q_p": [5, 10],
            "V_c": 2,
            "V_p": [1, 3],
            "CL": 1,
            "k_a": 5,
        },
    ],
)
def A1(request):
    return request.param

@pytest.fixture(scope="session")
def m1(A1):
    return pk.Model(
        Q_p=A1["Q_p"],
        V_c=A1["V_c"],
        V_p=A1["V_p"],
        CL=A1["CL"],
        k_a=A1["k_a"],
    )

class TestModel:
    """
    Tests the :class:`Model` class.
    """
    def test_create_model(self, A1, m1):
        """
        Tests Model creation.
        """
        npt.assert_array_equal(m1.Q_p, A1["Q_p"])
        assert m1.V_c == A1["V_c"]
        npt.assert_array_equal(m1.V_p, A1["V_p"])
        assert m1.CL == A1["CL"]
        assert m1.k_a == A1["k_a"]
        assert "central" in m1.compartment_names
        assert m1.dose_compartment_index == 0

    def test_compartment_names(self, A1, m1):
        """
        Test compartment names
        """
        if A1["k_a"] is None:
            assert m1.compartment_names[0] == "central"
            assert "absorption" not in m1.compartment_names
            assert m1.n_compartments == len(A1["Q_p"]) + 1
        else:
            assert m1.compartment_names[0] == "absorption"
            assert m1.compartment_names[1] == "central"
            assert m1.n_compartments == len(A1["Q_p"]) + 2

    def test_rhs_not_implemented_yet(self, A1, m1):
        """
        Test that calling rhs on the model yields a NotImplementedError
        if the peripheral compartments were not provided
        """
        if A1["Q_p"] is None:
            with pytest.raises(NotImplementedError):
                assert m1.rhs(0.0, [0.0])
