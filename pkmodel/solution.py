"""Numerical simulation and result handling for PK models."""

import itertools
from collections.abc import Sequence
from typing import TYPE_CHECKING, Self

import numpy as np
from scipy.integrate import solve_ivp

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .model import Model
    from .protocol import Protocol


class Solution:
    """Solve a PK model for an independently specified dosing protocol.

    Parameters
    ----------
    model : Model
        Defines compartments, PK parameters, and the ODE derivatives.
    protocol : Protocol
        Defines exact bolus events and constant-rate infusions.

    Attributes
    ----------
    t : numpy.ndarray or None
        Solution times in hours. With ``t_eval=None``, bolus events may
        appear twice to show the instantaneous change in quantity.
        (E.g. a bolus of 5 at time 2 would result in (t=2, q=...) and (t=2, q=...+5) both being recorded.)
    y : numpy.ndarray or None
        Compartment quantities in ng, shape (n_compartments, n_times).

    Notes
    -----
    Every compartment initially contains zero drug. At a bolus time,
    the dose is added instantaneously to ``model.dose_compartment_index``.
    If ``t_eval`` is provided, values at bolus times are *post-dose*.

    Infusions are integrated at their exact constant rates; the ODE
    solver is restarted at each infusion boundary and bolus event.
    """

    def __init__(self, model: "Model", protocol: "Protocol") -> None:
        self.model = model
        self.protocol = protocol
        self.t: np.ndarray | None = None
        self.y: np.ndarray | None = None

    def solve(
        self,
        t_span: tuple[float, float],
        t_eval: Sequence[float] | None = None,
    ) -> Self:
        """Numerically solve the model using SciPy's ``solve_ivp``.

        Parameters
        ----------
        t_span : (float, float)
            Start and end times (hours), with end strictly after start.
            Initial compartment quantities are zero except for any bolus
            scheduled at the start time.
        t_eval : sequence of float, optional
            Strictly increasing observation times within ``t_span``.
            Results at bolus times are after administration. If omitted,
            the solver's adaptive time points are retained, including
            both sides of each nonzero bolus jump.

        Returns
        -------
        Solution
            This object, with ``t`` and ``y`` populated.
        """
        start, end = map(float, t_span)
        if not np.isfinite(start) or not np.isfinite(end) or end <= start:
            raise ValueError("t_span must contain finite, increasing times")

        observation_times = None
        if t_eval is not None:
            observation_times = np.asarray(t_eval, dtype=float)
            if observation_times.ndim != 1 or observation_times.size == 0:
                raise ValueError("t_eval must be a nonempty 1D sequence")
            if not np.all(np.isfinite(observation_times)):
                raise ValueError("t_eval must contain only finite times")
            if np.any(np.diff(observation_times) <= 0):
                raise ValueError("t_eval must be strictly increasing")
            if observation_times[0] < start or observation_times[-1] > end:
                raise ValueError("t_eval times must lie within t_span")

        # Each interval has a constant infusion rate. Exact breakpoints
        # prevent adaptive integration from overlooking changes in dosing.
        events = [
            time
            for time in self.protocol.event_times()
            if start < time < end
        ]
        boundaries = [start, *events, end]

        state = np.zeros(self.model.n_compartments, dtype=float)
        dose_index = self.model.dose_compartment_index
        state[dose_index] += self.protocol.bolus_amount(start)

        if observation_times is None:
            output_times = [start]
            output_states = [state.copy()]
        else:
            output_quantities = np.empty(
                (self.model.n_compartments, len(observation_times)),
                dtype=float,
            )

        for left, right in itertools.pairwise(boundaries):
            # The rate is constant throughout this open interval. Using
            # its midpoint avoids evaluating a discontinuous input at
            # an endpoint inside solve_ivp's Runge-Kutta stages.
            rate = self.protocol.dose_rate(left + (right - left) / 2)

            result = solve_ivp(
                fun=lambda t, y, rate=rate: self.model.rhs(t, y, input_rate=rate),
                t_span=(left, right),
                y0=state,
                dense_output=observation_times is not None,
                rtol=1e-8,
                atol=1e-10,
            )
            if not result.success:
                raise RuntimeError(f"ODE integration failed: {result.message}")

            if observation_times is None:
                # Retain the solver's natural samples, excluding the
                # already-recorded starting point of each segment.
                output_times.extend(result.t[1:].tolist())
                output_states.extend(result.y[:, 1:].T.copy())
            else:
                # A point exactly on an event belongs to the NEXT
                # interval, after any bolus at that event has been applied.
                mask = (observation_times >= left) & (observation_times < right)
                if np.any(mask):
                    output_quantities[:, mask] = result.sol(observation_times[mask])

            state = result.y[:, -1].copy()

            # Apply a bolus as an exact change in state, not an ODE rate.
            bolus = self.protocol.bolus_amount(right)
            if bolus:
                state[dose_index] += bolus
                if observation_times is None:
                    # Duplicate the time to display a vertical jump.
                    output_times.append(right)
                    output_states.append(state.copy())

        if observation_times is None:
            self.t = np.asarray(output_times)
            self.y = np.column_stack(output_states)
        else:
            # The final endpoint has no following segment. It must be
            # sampled explicitly, after any bolus scheduled there.
            if observation_times[-1] == end:
                output_quantities[:, -1] = state
            self.t = observation_times.copy()
            self.y = output_quantities

        return self

    def plot(self, compartment: str = "central", ax: "Axes | None" = None) -> "Axes":
        """Plot drug quantity in the selected compartment (ng vs h).

        Parameters
        ----------
        compartment : str
            One of ``model.compartment_names`` (default: ``central``).
        ax : matplotlib.axes.Axes, optional
            Existing axes on which to draw. If omitted, create axes.

        Returns
        -------
        matplotlib.axes.Axes
            The axes containing the plot.
        """
        if self.t is None or self.y is None:
            raise RuntimeError("Call solve() before plot()")

        try:
            index = self.model.compartment_names.index(compartment)
        except ValueError as exc:
            raise ValueError(
                f"Unknown compartment {compartment!r}; "
                f"choose from {self.model.compartment_names}"
            ) from exc

        if ax is None:
            import matplotlib.pyplot as plt

            _, ax = plt.subplots()

        # Label bolus and infusions


        ax.plot(self.t, self.y[index], label=compartment)

        # Label bolus events
        for i in range(len(self.protocol.boluses)):
            ax.axvline(self.protocol.boluses[i][0], c='k', ls='--', alpha=.7, label=f'Bolus ({self.protocol.boluses[i][1]:,} ng)')

        # Show infusions
        for i in range(len(self.protocol.infusions)):
            ax.axvspan(self.protocol.infusions[i][0], self.protocol.infusions[i][1], alpha=0.5, color='lightgrey', label=f'Infusion ({self.protocol.infusions[i][2]:,} ng/hr)')
        ax.set_xlabel("Time (h)")
        ax.set_ylabel("Drug quantity (ng)")
        ax.legend()

        return ax
