"""Definition of a compartmental pharmacokinetic model."""

from collections.abc import Sequence


class Model:
    """Store PK parameters and define the future ODE interface.

    Parameters
    ----------
    V_c : float
        Central compartment volume in mL.
    CL : float
        Clearance from the central compartment in mL/h.
    V_p : sequence of float, optional
        Peripheral compartment volumes in mL.
    Q_p : sequence of float, optional
        Exchange clearances for peripheral compartments in mL/h.
    k_a : float, optional
        First-order absorption rate in 1/h. If provided, the model has
        a subcutaneous absorption compartment; otherwise it is IV.

    Notes
    -----
    State ordering is [central, peripheral_1, ...] for IV models and
    [absorption, central, peripheral_1, ...] for SC models. Doses enter
    the central compartment for IV, or the absorption compartment for SC.
    The right-hand side method is intentionally unimplemented in Phase 1.
    """

    def __init__(
        self,
        V_c: float,
        CL: float,
        V_p: Sequence[float] | None = None,
        Q_p: Sequence[float] | None = None,
        k_a: float | None = None,
    ) -> None:
        self.V_c = V_c
        self.CL = CL
        self.V_p = tuple(V_p) if V_p is not None else ()
        self.Q_p = tuple(Q_p) if Q_p is not None else ()
        self.k_a = k_a

    @property
    def compartment_names(self) -> tuple[str, ...]:
        """Names in the same order as ODE state vector entries."""
        names = ["central"]
        names.extend(f"peripheral_{i}" for i in range(1, len(self.V_p) + 1))
        if self.k_a is not None:
            names.insert(0, "absorption")
        return tuple(names)

    @property
    def n_compartments(self) -> int:
        """Number of state variables in the ODE system."""
        return len(self.compartment_names)

    @property
    def dose_compartment_index(self) -> int:
        """State index receiving doses: IV central or SC absorption."""
        return 0

    def rhs(self, t: float, y: Sequence[float], input_rate: float = 0.0) -> list[float]:
        """Return dq/dt (ng/h) given time, quantities (ng), and dose rate.

        Implement this in the Model development task. This method must
        not read a Protocol object; the Solution will supply input_rate.
        """
        if self.k_a is None: #AKA Intravenous dosing
            q_c, q_p1 = y
            transition = self.Q_p[0] * (q_c / self.V_c - q_p1 / self.V_p[0])

            dqc_dt = input_rate - q_c / self.V_c * self.CL - transition
            dqp1_dt = transition

            return [dqc_dt, dqp1_dt]
        else: #AKA Subcutaneous dosing
            q_0, q_c, q_p1 = y

            absorption = self.k_a * q_0
            transition = self.Q_p[0] * (q_c / self.V_c - q_p1 / self.V_p[0])

            dq0_dt = input_rate - absorption
            dqc_dt = absorption - q_c / self.V_c * self.CL - transition
            dqp1_dt = transition

            return [dq0_dt, dqc_dt, dqp1_dt]

