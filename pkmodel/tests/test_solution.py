import numpy as np
import numpy.testing as npt
import pytest

import pkmodel as pk


@pytest.fixture(scope="session")
def m1():
    return pk.Model(V_c=1, CL=1)


@pytest.fixture(scope="session")
def p1():
    return pk.Protocol(boluses=[(0, 10), (1, 5)])


@pytest.fixture
def s1(m1, p1):
    return pk.Solution(m1, p1)


class TestSolution:
    """Tests the :class:`Solution` class."""

    def test_create_solution(self, s1, m1, p1):
        """Tests Solution creation before solving."""
        assert s1.model is m1
        assert s1.protocol is p1
        assert s1.t is None
        assert s1.y is None

    def test_solve_boluses_at_observation_times(self, s1):
        """Bolus observations show the quantity after each dose."""
        assert s1.solve((0, 2), t_eval=[0, 1, 2]) is s1
        npt.assert_array_equal(s1.t, [0, 1, 2])
        npt.assert_allclose(
            s1.y,
            [[10, 10 * np.exp(-1) + 5, (10 * np.exp(-1) + 5) * np.exp(-1)]],
            rtol=1e-6,
        )

    def test_solve_without_observation_times(self, s1):
        """Adaptive output includes both sides of an interior bolus."""
        assert s1.solve((0, 2)) is s1
        event_indices = np.flatnonzero(s1.t == 1)
        assert len(event_indices) == 2
        npt.assert_allclose(np.diff(s1.y[0, event_indices]), [5], rtol=1e-10)
        npt.assert_allclose(s1.y[0, 0], 10)

    def test_solve_infusion(self, m1):
        """An infusion stops contributing at its exact end time."""
        solution = pk.Solution(m1, pk.Protocol(infusions=[(0, 1, 10)]))
        solution.solve((0, 2), t_eval=[0, 1, 2])
        npt.assert_array_equal(solution.t, [0, 1, 2])
        npt.assert_allclose(
            solution.y,
            [[0, 10 * (1 - np.exp(-1)), 10 * (1 - np.exp(-1)) * np.exp(-1)]],
            rtol=1e-6,
            atol=1e-8,
        )

    def test_solve_bolus_at_end(self, m1):
        """A bolus at the final observation time is included."""
        solution = pk.Solution(m1, pk.Protocol(boluses=[(2, 5)]))
        solution.solve((0, 2), t_eval=[0, 2])
        npt.assert_array_equal(solution.y, [[0, 5]])

    @pytest.mark.parametrize(
        "t_span, t_eval",
        [
            ((1, 1), None),
            ((0, np.inf), None),
            ((0, 2), []),
            ((0, 2), [1, 1]),
            ((0, 2), [-1, 1]),
            ((0, 2), [0, np.nan]),
        ],
    )
    def test_invalid_solve_times(self, s1, t_span, t_eval):
        """Invalid spans and observation times are rejected."""
        with pytest.raises(ValueError):
            s1.solve(t_span, t_eval=t_eval)

    def test_plot(self, s1):
        """Plot uses solved quantities and labels the dosing events."""
        import matplotlib.pyplot as plt

        with pytest.raises(RuntimeError, match="Call solve"):
            s1.plot(s1.protocol)

        s1.solve((0, 2), t_eval=[0, 1, 2])
        fig, ax = plt.subplots()
        try:
            assert s1.plot(s1.protocol, ax=ax) is ax
            npt.assert_array_equal(ax.lines[0].get_xdata(), s1.t)
            npt.assert_allclose(ax.lines[0].get_ydata(), s1.y[0])
            assert ax.get_xlabel() == "Time (h)"
            assert ax.get_ylabel() == "Drug quantity (ng)"
            assert any(line.get_label() == "Bolus (10 ng)" for line in ax.lines)
            with pytest.raises(ValueError, match="Unknown compartment"):
                s1.plot(s1.protocol, compartment="missing", ax=ax)
        finally:
            plt.close(fig)
