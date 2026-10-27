"""Visualise a PK model and its dosing protocol as a compartment diagram.

The drawing functions do not solve ODEs. Matplotlib is the only requirement.
"""

from __future__ import annotations

from textwrap import fill
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch, Rectangle

if TYPE_CHECKING:
    from .model import Model
    from .protocol import Protocol


def plot_model_diagram(
    model: Model,
    protocol: Protocol | None = None,
    ax: Axes | None = None,
) -> Axes:
    """Draw compartments, drug transport, clearance and optional dose schedule.

    Parameters
    ----------
    model : Model
        PK model containing ``V_c``, ``CL``, ``V_p``, ``Q_p`` and ``k_a``.
    protocol : Protocol, optional
        Dosing protocol to summarise beneath the compartment diagram.
    ax : matplotlib.axes.Axes, optional
        Axes on which to draw. If omitted, a new figure is created.

    Returns
    -------
    matplotlib.axes.Axes
        The axes containing the finished drawing. Call ``plt.show()``
        to display it, or ``ax.figure.savefig(...)`` to save it.

    Notes
    -----
    This is a schematic of a *model*, not a plot of calculated quantities.
    Peripheral compartments connect only to the central compartment.
    Bolus amounts (ng) and infusion rates (ng/h) are labelled separately.
    """
    n_peripheral = len(model.V_p)
    is_sc = model.k_a is not None

    if ax is None:
        width = 12 if is_sc else (10 if n_peripheral else 8)
        height = max(5.3, 5.0 + max(0, n_peripheral - 2) * 1.15)
        _, ax = plt.subplots(figsize=(width, height))

    central_x = 0.0
    peripheral_x = 4.7
    absorption_x = -4.1
    central_width = 2.65
    peripheral_width = 2.85
    absorption_width = 2.65
    box_height = 1.15

    def draw_box(x: float, y: float, w: float, title: str, details: str, dashed: bool = False) -> None:
        ax.add_patch(
            Rectangle(
                (x - w / 2, y - box_height / 2),
                w,
                box_height,
                linewidth=1.8,
                linestyle="--" if dashed else "-",
                edgecolor="black",
                facecolor="white",
            )
        )
        ax.text(x, y + 0.19, title, ha="center", va="center", fontsize=10)
        ax.text(x, y - 0.18, details, ha="center", va="center", fontsize=12)

    def draw_arrow(start, end, label: str | None = None, label_pos=None, both: bool = False) -> None:
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="<->" if both else "->",
                mutation_scale=16,
                linewidth=1.7,
                color="black",
            )
        )
        if label is not None:
            if label_pos is None:
                label_pos = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.25)
            ax.text(*label_pos, label, ha="center", va="center", fontsize=11)

    draw_box(central_x, 0.0, central_width, "Central compartment", rf"$V_c={model.V_c:g}\,\mathrm{{mL}},\ q_c$")

    # Peripherals are stacked vertically, each linked directly to central.
    spacing = 1.7
    peripheral_ys = [(n_peripheral - 1 - 2 * i) * spacing / 2 for i in range(n_peripheral)]
    for i, (volume, exchange, y) in enumerate(zip(model.V_p, model.Q_p, peripheral_ys), start=1):
        draw_box(
            peripheral_x, y, peripheral_width,
            f"Peripheral compartment {i}",
            rf"$V_{{p{i}}}={volume:g}\,\mathrm{{mL}},\ q_{{p{i}}}$",
            dashed=True,
        )
        # Use a different location on the central box edge for each link.
        attachment_y = max(-0.42, min(0.42, y * 0.22))
        arrow_mid_y = (attachment_y + y) / 2
        draw_arrow(
            (central_x + central_width / 2 + 0.05, attachment_y),
            (peripheral_x - peripheral_width / 2 - 0.07, y),
            both=True,
            label=rf"$Q_{{p{i}}}={exchange:g}\,\mathrm{{mL/h}}$",
            label_pos=(2.35, arrow_mid_y + 0.27),
        )

    # SC doses enter absorption; IV doses enter the central compartment.
    dose_x = absorption_x if is_sc else central_x
    if is_sc:
        draw_box(absorption_x, 0.0, absorption_width, "Absorption compartment", r"$q_0$")
        draw_arrow(
            (absorption_x + absorption_width / 2 + 0.05, 0.0),
            (central_x - central_width / 2 - 0.05, 0.0),
            label=rf"$k_a={model.k_a:g}\,\mathrm{{h^{{-1}}}}$",
            label_pos=(-2.05, 0.35),
        )

    draw_arrow((dose_x, 1.67), (dose_x, box_height / 2 + 0.06))
    ax.text(dose_x, 1.89, "Dose", ha="center", va="center", fontsize=12)

    draw_arrow((central_x, -box_height / 2 - 0.06), (central_x, -1.65))
    ax.text(0.42, -1.13, rf"$CL={model.CL:g}\,\mathrm{{mL/h}}$", ha="left", va="center", fontsize=11)
    ax.text(central_x, -1.91, "Clearance", ha="center", va="center", fontsize=11)

    left_edge = -5.8 if is_sc else -2.75
    right_edge = 6.45 if n_peripheral else 2.75
    top_edge = max(2.55, max(peripheral_ys, default=0.0) + 1.05)
    bottom_of_boxes = min(-2.35, min(peripheral_ys, default=0.0) - 0.65)

    if protocol is not None:
        # Summarise the actual events, never imply a bolus is a rate.
        parts = []
        if protocol.boluses:
            parts.append(
                "Boluses: " + ", ".join(
                    f"{amount:g} ng at {time:g} h"
                    for time, amount in protocol.boluses
                )
            )
        if protocol.infusions:
            parts.append(
                "Infusions: " + ", ".join(
                    f"{rate:g} ng/h from {start:g} to {end:g} h"
                    for start, end, rate in protocol.infusions
                )
            )
        if not parts:
            parts.append("No doses scheduled")
        wrap_width = 85 if is_sc else (62 if n_peripheral else 42)
        note = "\n".join(fill(part, width=wrap_width) for part in parts)
        lines = len(note.splitlines())
        note_y = bottom_of_boxes - 0.38
        ax.text(
            (left_edge + right_edge) / 2,
            note_y,
            note,
            ha="center",
            va="top",
            fontsize=9.5,
            linespacing=1.55,
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "white", "edgecolor": "0.7"},
        )
        bottom_edge = note_y - (lines * 0.27 + 0.65)
    else:
        bottom_edge = bottom_of_boxes - 0.22

    ax.set_xlim(left_edge, right_edge)
    ax.set_ylim(bottom_edge, top_edge)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    return ax
