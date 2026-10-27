"""Interactive comparison demo for the pkmodel package.

Run from the repository root with ``streamlit run app.py``.
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

import pkmodel as pk


def model_parameters(label, peripheral_count, use_absorption, q_defaults):
    """Collect parameters for one model from the comparison form."""
    st.subheader(label)
    central_volume = st.number_input(
        "{} central volume (mL)".format(label),
        min_value=0.000001,
        value=1.0,
        step=0.1,
        key="{}_central_volume".format(label),
    )
    clearance = st.number_input(
        "{} clearance (mL/h)".format(label),
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="{}_clearance".format(label),
    )

    peripheral_volumes = []
    exchange_clearances = []
    for index in range(peripheral_count):
        peripheral_volumes.append(
            st.number_input(
                "{} peripheral {} volume (mL)".format(label, index + 1),
                min_value=0.000001,
                value=1.0,
                step=0.1,
                key="{}_volume_{}".format(label, index),
            )
        )
        exchange_clearances.append(
            st.number_input(
                "{} peripheral {} exchange clearance (mL/h)".format(
                    label, index + 1
                ),
                min_value=0.0,
                value=q_defaults[index],
                step=0.1,
                key="{}_exchange_{}".format(label, index),
            )
        )

    absorption_rate = None
    if use_absorption:
        absorption_rate = st.number_input(
            "{} absorption rate (1/h)".format(label),
            min_value=0.000001,
            value=1.0,
            step=0.1,
            key="{}_absorption_rate".format(label),
        )

    return {
        "V_c": central_volume,
        "CL": clearance,
        "V_p": peripheral_volumes,
        "Q_p": exchange_clearances,
        "k_a": absorption_rate,
    }


st.set_page_config(page_title="PK model comparison")
st.title("PK model comparison")
st.write(
    "Explore how model parameters change the simulated compartment amounts. "
    "Both models use the same dosing protocol and simulation interval."
)
st.caption(
    "Educational demonstration only. This app is not intended for clinical "
    "or treatment decisions."
)

with st.form("model_comparison"):
    st.subheader("Simulation and dosing")
    control_columns = st.columns(4)
    with control_columns[0]:
        duration = st.number_input(
            "Duration (h)", min_value=0.1, value=24.0, step=1.0
        )
    with control_columns[1]:
        sample_count = st.number_input(
            "Output points", min_value=2, max_value=2000, value=300, step=50
        )
    with control_columns[2]:
        peripheral_count = st.number_input(
            "Peripheral compartments",
            min_value=0,
            max_value=3,
            value=1,
            step=1,
        )
    with control_columns[3]:
        use_absorption = st.checkbox("Use SC absorption compartment")

    infusion_columns = st.columns(2)
    with infusion_columns[0]:
        infusion_enabled = st.checkbox("Apply continuous infusion", value=True)
    with infusion_columns[1]:
        infusion_rate = st.number_input(
            "Infusion rate (ng/h)", min_value=0.0, value=1.0, step=0.1
        )

    model_columns = st.columns(2)
    with model_columns[0]:
        parameters_a = model_parameters(
            "Model A",
            peripheral_count,
            use_absorption,
            [1.0, 2.0, 3.0],
        )
    with model_columns[1]:
        parameters_b = model_parameters(
            "Model B",
            peripheral_count,
            use_absorption,
            [2.0, 4.0, 6.0],
        )

    submitted = st.form_submit_button("Simulate and compare")

if submitted:
    infusions = (
        [(0.0, float(duration), float(infusion_rate))]
        if infusion_enabled and infusion_rate > 0
        else []
    )
    protocol = pk.Protocol(infusions=infusions)
    model_a = pk.Model(**parameters_a)
    model_b = pk.Model(**parameters_b)
    evaluation_times = np.linspace(0.0, float(duration), int(sample_count))

    try:
        solution_a = pk.Solution(model_a, protocol).solve(
            (0.0, float(duration)), t_eval=evaluation_times
        )
        solution_b = pk.Solution(model_b, protocol).solve(
            (0.0, float(duration)), t_eval=evaluation_times
        )
    except NotImplementedError as error:
        st.error(
            "The package simulation is not implemented yet, so the app "
            "cannot run this comparison. Complete Model.rhs and "
            "Solution.solve first. Details: {}".format(error)
        )
        st.stop()

    figure, axes = plt.subplots()
    for label, solution in (("Model A", solution_a), ("Model B", solution_b)):
        for index, compartment in enumerate(solution.model.compartment_names):
            axes.plot(
                solution.t,
                solution.y[index],
                label="{} - {}".format(label, compartment),
            )
    axes.set_xlabel("Time (h)")
    axes.set_ylabel("Drug amount (ng)")
    axes.set_title("Compartment amounts over time")
    axes.legend()
    axes.grid(True, alpha=0.3)
    st.pyplot(figure)
    plt.close(figure)

    central_index_a = model_a.compartment_names.index("central")
    central_index_b = model_b.compartment_names.index("central")
    central_a = solution_a.y[central_index_a, -1]
    central_b = solution_b.y[central_index_b, -1]
    metric_columns = st.columns(3)
    metric_columns[0].metric("Model A central at end", "{:.3f} ng".format(central_a))
    metric_columns[1].metric("Model B central at end", "{:.3f} ng".format(central_b))
    metric_columns[2].metric(
        "Difference (B - A)", "{:+.3f} ng".format(central_b - central_a)
    )