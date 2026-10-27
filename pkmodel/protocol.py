
"""Dosing schedules independent of the PK model."""

from collections.abc import Sequence
from math import isfinite


class Protocol:
    """Store exact bolus events and constant-rate infusions.

    Parameters
    ----------
    boluses : sequence of (time, amount), optional
        Instantaneous doses: time in hours, amount in ng.
    infusions : sequence of (start, end, rate), optional
        Continuous inputs: start/end in hours, rate in ng/h.

    Notes
    -----
    Infusions are active on the interval [start, end).
    Boluses are instantaneous events, not continuous rates.
    The Model determines which compartment receives the dose.
    """

    def __init__(
        self,
        boluses: Sequence[tuple[float, float]] | None = None,
        infusions: Sequence[tuple[float, float, float]] | None = None,
    ) -> None:
        self.boluses = tuple(boluses) if boluses is not None else ()
        self.infusions = tuple(infusions) if infusions is not None else ()

        # Validate boluses
        for time, amount in self.boluses:
            if not isfinite(time) or time < 0:
                raise ValueError("Bolus times must be finite and non-negative")
            if not isfinite(amount) or amount < 0:
                raise ValueError("Bolus amounts must be finite and non-negative")

<<<<<<< HEAD
        Implement in the Protocol development task. The bolus events
        are handled separately by Solution, not as part of dose_rate.
        Infusion intervals use start <= t < end.
        """
        total_rate = 0.0

        for start, end, rate in self.infusions: #no boluses as only infusions as given continuously
            if start <= t < end:
                total_rate += rate
        return total_rate
    
    # def dose(self, t, X):
    #     """Dose function to be evaluated at all times t in [0,1] when solving ODEs

    #     Args:
    #         t (float): time value, between 0 and 1
    #         X (float): magnitude of dosage applied at all relevant times

    #     Returns:
    #         float: amount of drug administered at time t
    #     """
    #     if self.dose_on == 0:
    #         return X * (t == 0)
    #     else:
    #         return X * ((self.eval_subdiv - 1) * t % (self.dose_on
    #                     + self.dose_off) < self.dose_on)
=======
        # Validate infusions
        for start, end, rate in self.infusions:
            if not all(isfinite(x) for x in (start, end, rate)):
                raise ValueError("Infusion values must be finite")
            if start < 0 or end <= start:
                raise ValueError("Infusions require 0 <= start < end")
            if rate < 0:
                raise ValueError("Infusion rates must be non-negative")

    def dose_rate(self, t: float) -> float:
        """Return total continuous infusion rate at time t (ng/h)."""
        return sum(
            rate
            for start, end, rate in self.infusions
            if start <= t < end
        )

    def bolus_amount(self, t: float) -> float:
        """Return total bolus amount scheduled exactly at t (ng)."""
        return sum(
            amount
            for time, amount in self.boluses
            if time == t
        )

    def event_times(self) -> tuple[float, ...]:
        """Return sorted unique times at which dosing changes."""
        times = {time for time, _ in self.boluses}

        for start, end, _ in self.infusions:
            times.update((start, end))

        return tuple(sorted(times))
>>>>>>> ed89077ed5ce2a7251f07859621397ffe8c5ee78
