"""Dosing schedules independent of the PK model."""

from collections.abc import Sequence


class Protocol:
    """Store a schedule of bolus doses and continuous infusions.

    Parameters
    ----------
    boluses : sequence of (time, amount), optional
        Instantaneous doses: time in h, amount in ng.
    infusions : sequence of (start, end, rate), optional
        Constant infusions: start/end in h, rate in ng/h.

    Notes
    -----
    The Model chooses which compartment receives the dose. This class
    does not depend on Model or Solution. Time is measured in hours.
    """

    def __init__(
        self,
        boluses: Sequence[tuple[float, float]] | None = None,
        infusions: Sequence[tuple[float, float, float]] | None = None,
    ) -> None:
        self.boluses = tuple(boluses) if boluses is not None else ()
        self.infusions = tuple(infusions) if infusions is not None else ()

    def dose_rate(self, t: float) -> float:
        """Return continuous dose rate at time t in ng/h.

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