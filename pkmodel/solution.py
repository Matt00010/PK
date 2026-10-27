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

    

