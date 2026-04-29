import streamlit as st
import pandas as pd

from src.core.group_models import SCENARIOS, annual_savings, discounted_annual_savings, subsidy_eur, economic_utility_for_year

st.set_page_config(page_title="PV ROI", layout="wide")
st.title("PV ROI Calculator")
st.caption("Notebook-aligned farm-scale PV economics based on the group WP4 formulations.")

scenario_keys = [k for k in SCENARIOS.keys()]
labels = {k: SCENARIOS[k].name for k in scenario_keys}

with st.form("roi_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        scenario_key = st.selectbox("Group scenario", scenario_keys, format_func=lambda x: labels[x])
    scenario = SCENARIOS[scenario_key]
    with c2:
        year = st.selectbox("Year", scenario.years)
    with c3:
        use_custom = st.checkbox("Override notebook defaults", value=False)

    if use_custom:
        c4, c5, c6 = st.columns(3)
        with c4:
            annual_load_kwh = st.number_input("Annual electricity consumption (kWh)", 1.0, 1e8, float(scenario.annual_load_kwh), 100.0)
            annual_solar_kwh = st.number_input("Annual solar generation (kWh)", 1.0, 1e8, float(scenario.annual_solar_generation_kwh), 100.0)
        with c5:
            electricity_price = st.number_input("Electricity price (c€/kWh)", 0.0, 500.0, float(scenario.energy_prices_cents[year]), 0.1)
            pv_cost = st.number_input("PV cost (€)", 0.0, 1e8, float(scenario.pv_cost_eur[year]), 100.0)
        with c6:
            subsidy_rate = st.slider("Subsidy rate", 0.0, 1.0, float(scenario.subsidy_rate.get(year, 0.0)), 0.05)
            discount_rate = st.number_input("Discount rate", 0.0, 1.0, float(scenario.discount_rate), 0.01)
            lifespan = st.number_input("Lifespan (years)", 1, 100, int(scenario.lifespan_years))
    submitted = st.form_submit_button("Calculate notebook-aligned ROI")

if submitted:
    if use_custom:
        a_sav = annual_savings(annual_load_kwh, annual_solar_kwh, electricity_price)
        maintenance = 0.02 * pv_cost
        discounted = discounted_annual_savings(a_sav, maintenance, discount_rate, int(lifespan))
        subsidy = subsidy_eur(pv_cost, subsidy_rate)
        economic_utility = discounted + subsidy - pv_cost
        payload = {
            "Annual load (kWh)": annual_load_kwh,
            "Annual solar generation (kWh)": annual_solar_kwh,
            "Electricity price (c€/kWh)": electricity_price,
            "PV cost (€)": pv_cost,
            "Subsidy rate": subsidy_rate,
            "Discount rate": discount_rate,
            "Lifespan (years)": lifespan,
        }
    else:
        a_sav = annual_savings(scenario.annual_load_kwh, scenario.annual_solar_generation_kwh, scenario.energy_prices_cents[year])
        pv_cost = scenario.pv_cost_eur[year]
        maintenance = scenario.maintenance_rate * pv_cost
        discounted = discounted_annual_savings(a_sav, maintenance, scenario.discount_rate, scenario.lifespan_years)
        subsidy = subsidy_eur(pv_cost, scenario.subsidy_rate.get(year, 0.0))
        economic_utility = economic_utility_for_year(scenario, year)
        payload = {
            "Annual load (kWh)": scenario.annual_load_kwh,
            "Annual solar generation (kWh)": scenario.annual_solar_generation_kwh,
            "Electricity price (c€/kWh)": scenario.energy_prices_cents[year],
            "PV cost (€)": pv_cost,
            "Subsidy rate": scenario.subsidy_rate.get(year, 0.0),
            "Discount rate": scenario.discount_rate,
            "Lifespan (years)": scenario.lifespan_years,
        }

    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual savings", f"€{a_sav:,.0f}")
    c2.metric("Annual maintenance", f"€{maintenance:,.0f}")
    c3.metric("Discounted savings", f"€{discounted:,.0f}")
    c4.metric("Economic utility", f"€{economic_utility:,.0f}")

    c5, c6 = st.columns(2)
    c5.metric("PV cost", f"€{pv_cost:,.0f}")
    c6.metric("Subsidy", f"€{subsidy:,.0f}")

    st.markdown("### Active assumptions")
    st.dataframe(pd.DataFrame([payload]), use_container_width=True)
else:
    st.info("Choose a group scenario and a year to reproduce the WP4 ROI calculation.")
