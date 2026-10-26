"""Numerical simulation and result handling for PK models."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from .model import Model
    from .protocol import Protocol


class Solution:
    """Link a Model to a Protocol and eventually solve the ODE system.

    Parameters
    ----------
    model : Model
        PK model, independently configured.
    protocol : Protocol
        Dosing schedule, independently configured.

    Attributes
    ----------
    t : array-like or None
        Evaluation times in hours after solve() succeeds.
    y : array-like or None
        Compartment quantities in ng, shape (n_compartments, n_times).
    """

    def __init__(self, model: "Model", protocol: "Protocol") -> None:
        self.model = model
        self.protocol = protocol
        self.t = None
        self.y = None

    def solve(
        self,
        t_span: tuple[float, float],
        t_eval: Sequence[float] | None = None,
    ) -> Self:
        """Numerically solve the model over t_span (hours).

        Implement in the Solution task using scipy.integrate.solve_ivp.
        Later, apply boluses as instantaneous state jumps; split the
        integration at bolus and infusion boundaries. Store t and y,
        then return self.
        """
        raise NotImplementedError("Solution.solve is a Phase 3 task")

    def plot(self, compartment: str = "central", ax=None):
        """Plot an existing solution; accept an optional Matplotlib Axes.

        Implement in the plotting task, after numerical results exist.
        Return the Matplotlib Axes used for the plot.
        """
        raise NotImplementedError("Solution.plot is a later task")
