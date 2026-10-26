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
        raise NotImplementedError("Protocol.dose_rate is a Phase 2 task")
