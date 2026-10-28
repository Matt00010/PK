import numpy as np
import numpy.testing as npt
import pytest

import pkmodel as pk

params = [
    {
        "boluses":
        [
            (1, 1),
            (1, 2),
            (5, 5)
        ],
        "infusions":
        [
            (0, 5, 5),
            (4, 10, 1)
        ],
        "times": [1, 4.5, 6],
        "expected_dose_rate": [5, 6, 1],
        "expected_bolus_amount": [3, 0, 0],
        "expected_times": (0, 1, 4, 5, 10)
    },
    {
        "boluses":
        [
            (-1, 1),
            (2, -2),
        ],
        "infusions":
        [
            (0, 2, np.nan),
            (np.nan, 1, 1),
            (1, np.nan, 3),
            (-6, 1, 1),
            (1, -1, 1),
        ],
        "times": None,
        "expected_dose_rate": None,
        "expected_bolus_amount": None,
        "expected_times": None
    },
    {
        "boluses": None,
        "infusions": None,
        "times": [1, 4.5, 6],
        "expected_dose_rate": [0, 0, 0],
        "expected_bolus_amount": [0, 0, 0],
        "expected_times": None
    }
]

@pytest.fixture(
    scope="session",
    params=[
        params[0], params[2]
    ]
)
def A1(request):
    return request.param

@pytest.fixture(
        scope="session",
        params=[params[1]]
)
def invalid_params(request):
    return request.param

@pytest.fixture(scope="session")
def p1(A1):
    return pk.Protocol(
        boluses=A1["boluses"],
        infusions=A1["infusions"],
    )

class TestProtocol:
    """
    Tests the :class:`Protocol` class.
    """
    def test_create_protocol(self, A1):
        """
        Tests Protocol creation.
        """

        p = pk.Protocol(A1["boluses"], A1["infusions"])
        if A1["boluses"] is None:
            assert p.boluses == ()
        else:
            npt.assert_array_equal(p.boluses, A1["boluses"])

        if A1["infusions"] is None:
            assert p.infusions == ()
        else:
            npt.assert_array_equal(p.infusions, A1["infusions"])

    def test_invalid_boluses(self, invalid_params):
        for bolus in invalid_params["boluses"]:
            with pytest.raises(ValueError):
                pk.Protocol(boluses=[bolus])

    def test_invalid_infusions(self, invalid_params):
        for infusion in invalid_params["infusions"]:
            with pytest.raises(ValueError):
                pk.Protocol(infusions=[infusion])

    def test_dose_rate(self, A1, p1):
        """
        Test dose rates of protocol
        """
        for time, expected in zip(A1["times"], A1["expected_dose_rate"]):
            assert p1.dose_rate(time) == expected

    def test_bolus_amount(self, A1, p1):
        """
        Test bolus amounts of protocol
        """
        for time, expected in zip(A1["times"], A1["expected_bolus_amount"]):
            assert p1.bolus_amount(time) == expected

    def test_event_times(self, A1, p1):
        """
        Test event times of protocol
        """
        event_times = p1.event_times()

        if A1["expected_times"] is None:
            assert isinstance(event_times, tuple) and len(event_times) == 0
        else:
            npt.assert_array_equal(event_times, A1["expected_times"])
