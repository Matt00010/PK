"""Definition of a compartmental pharmacokinetic model."""

from collections.abc import Sequence
from math import isfinite


class Model:
    """Linear compartmental pharmacokinetic model.

    Parameters
    ----------
    V_c : float
        Central compartment volume in mL (strictly positive).
    CL : float
        Clearance from the central compartment in mL/h (non-negative).
    V_p : sequence of float, optional
        Peripheral compartment volumes in mL (strictly positive).
    Q_p : sequence of float, optional
        Exchange clearances in mL/h (non-negative), one per peripheral.
    k_a : float, optional
        First-order absorption rate in 1/h (strictly positive). If provided,
        a subcutaneous absorption compartment precedes the central compartment.

    Notes
    -----
    IV state ordering: [central, peripheral_1, peripheral_2, ...].
    SC state ordering: [absorption, central, peripheral_1, ...].
    Drug is administered into the compartment at dose_compartment_index.
    Quantities are in ng; rates returned by rhs are in ng/h.
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

        if not isfinite(self.V_c) or self.V_c <= 0:
            raise ValueError("V_c must be positive and finite")
        if not isfinite(self.CL) or self.CL < 0:
            raise ValueError("CL must be non-negative and finite")
        if len(self.V_p) != len(self.Q_p):
            raise ValueError("V_p and Q_p must have the same length")
        if any(not isfinite(volume) or volume <= 0 for volume in self.V_p):
            raise ValueError("Peripheral volumes must be positive and finite")
        if any(not isfinite(clearance) or clearance < 0 for clearance in self.Q_p):
            raise ValueError("Exchange clearances must be non-negative and finite")
        if self.k_a is not None and (not isfinite(self.k_a) or self.k_a <= 0):
            raise ValueError("k_a must be positive and finite")

    @property
    def compartment_names(self) -> tuple[str, ...]:
        """Compartment names in the same order as the ODE state vector."""
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
        """Index of the compartment receiving IV or SC doses."""
        return 0

    def rhs(self, t: float, y: Sequence[float], input_rate: float = 0.0) -> list[float]:
        """Return rates of change of all compartment quantities (ng/h).

        Parameters
        ----------
        t : float
            Current time in h (accepted for the solve_ivp interface).
        y : sequence of float
            Drug quantities (ng), ordered according to compartment_names.
        input_rate : float, optional
            Continuous drug input in ng/h, supplied by Solution from Protocol.

        Returns
        -------
        list of float
            Time derivatives in ng/h, with the same ordering as ``y``.
        """
        if len(y) != self.n_compartments:
            raise ValueError(
                f"Expected {self.n_compartments} quantities, received {len(y)}"
            )

        # For SC dosing, the initial state is an absorption compartment.
        if self.k_a is None:
            q_c = y[0]
            q_p = y[1:]
            absorption_rate = 0.0
        else:
            q_abs = y[0]
            q_c = y[1]
            q_p = y[2:]
            absorption_rate = self.k_a * q_abs

        central_concentration = q_c / self.V_c
        dqc_dt = absorption_rate - self.CL * central_concentration
        peripheral_rates = []

        for amount, volume, exchange in zip(q_p, self.V_p, self.Q_p):
            transfer = exchange * (central_concentration - amount / volume)
            dqc_dt -= transfer
            peripheral_rates.append(transfer)

        if self.k_a is None:
            return [dqc_dt + input_rate, *peripheral_rates]

        return [input_rate - absorption_rate, dqc_dt, *peripheral_rates]
