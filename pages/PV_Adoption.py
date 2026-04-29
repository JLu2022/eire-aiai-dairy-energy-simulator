import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from src.core.group_models import SCENARIOS, simulate_group_scenario, scenario_year_table

st.set_page_config(page_title="PV Adoption Simulation", layout="wide")
st.title("PV Adoption Model")
st.caption("Research-mode implementation aligned to the group WP4 notebook scenarios.")

scenario_labels = {k: v.name for k, v in SCENARIOS.items()}

with st.form("sim_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        scenario_key = st.selectbox("Group scenario", list(scenario_labels.keys()), format_func=lambda x: scenario_labels[x])
        seed = st.number_input("Random seed", 0, 999999, 42)
    selected = SCENARIOS[scenario_key]
    with c2:
        total_farms = st.number_input("Total farms", 1, 500000, int(selected.total_farmers), step=100)
        initial_adopters = st.number_input("Initial adopters", 0, int(total_farms), int(min(selected.initial_adopters, total_farms)), step=10)
    with c3:
        st.markdown("**Notebook defaults**")
        st.write(f"Years: {selected.years[0]}–{selected.years[-1]}")
        st.write(f"Lifespan: {selected.lifespan_years} years")
        st.write(f"Discount rate: {selected.discount_rate:.2f}")
    submitted = st.form_submit_button("Run group scenario")

if submitted:
    result = simulate_group_scenario(scenario_key, seed=int(seed), total_farmers=int(total_farms), initial_adopters=int(initial_adopters))
    adoption_curve = result["adoption_rate"]
    cum_curve = result["cumulative"]
    years = result["years"]

    st.subheader("Results")
    k1, k2, k3 = st.columns(3)
    k1.metric("Final adoption rate", f"{adoption_curve[-1] * 100:.1f}%")
    k2.metric("Cumulative adoptions", f"{int(cum_curve[-1])}")
    k3.metric("Scenario", result['scenario'].name)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("### Adoption rate over time")
        fig1, ax1 = plt.subplots()
        ax1.plot(years, adoption_curve, marker='o')
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Adoption rate")
        ax1.set_xticks(years)
        st.pyplot(fig1, clear_figure=True)

    with c2:
        st.markdown("### Cumulative adoptions")
        fig2, ax2 = plt.subplots()
        ax2.plot(years, cum_curve, marker='o')
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Number of farmers")
        ax2.set_xticks(years)
        st.pyplot(fig2, clear_figure=True)

    st.markdown("### Year-by-year economic inputs and probabilities")
    df = pd.DataFrame(scenario_year_table(scenario_key))
    df["adoption_probability"] = df["adoption_probability"].map(lambda x: round(float(x), 4))
    st.dataframe(df, use_container_width=True)
else:
    st.info("Choose a WP4 scenario and run the simulation.")
