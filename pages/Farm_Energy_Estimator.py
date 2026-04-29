import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.core.simulate import simulate_one_day

st.set_page_config(page_title="Farm Energy Estimator", layout="wide")
st.title("Farm Energy Estimator")

with st.form("inputs"):
    col1, col2, col3 = st.columns(3)
    with col1:
        n_cows = st.number_input("# Cows", 1, 500, 55, step=1)
        n_mu = st.number_input("# Milking Units", 1, 60, 10, step=1)
    with col2:
        month = st.selectbox("Month", list(range(1, 13)), index=0)
        day = st.number_input("Day", 1, 31, 15, step=1)
    with col3:
        morning = st.slider("Morning milking start (hour)", 0, 23, 7, step=1)
        evening = st.slider("Evening milking start (hour)", 0, 23, 17, step=1)

    col4, col5 = st.columns(2)
    with col4:
        cooling = st.selectbox("Milk cooling system", ["DX", "IB"], index=0)
    with col5:
        e_water = st.selectbox("Electric water heating", ["YES", "NO"], index=0)

    submitted = st.form_submit_button("Run estimation")

if submitted:
    with st.spinner("Simulating today’s 24h load..."):
        res = simulate_one_day(
            n_cows=n_cows,
            n_milking_units=n_mu,
            month=month,
            day=day,
            start_morning=morning,
            start_evening=evening,
            milk_cooling_system=cooling,
            electric_water_heating=e_water,
        )

    # ---- KPIs
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total energy (kWh)", f"{res.total_wh / 1000:.1f}")
    with k2:
        st.metric("Peak power (kW)", f"{res.peak_w / 1000:.2f}")
    with k3:
        st.metric("Peak hour", f"{res.peak_hour}:00")

    # ---- Total load curve
    # st.markdown("### Hourly load (kWh)")
    hours = list(range(24))
    fig1, ax1 = plt.subplots()
    # print(res.hourly_total)
    # print(type(res.hourly_total[0]))
    # print(np.round(np.array(res.hourly_total, dtype=float), 2))
    ax1.plot(hours, np.round(np.array(res.hourly_total, dtype=float)/1000, 2), linewidth=3)
    ax1.fill_between(hours, np.round(np.array(res.hourly_total, dtype=float)/1000, 2), alpha=0.2)

    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Load (kWh)")
    ax1.grid(axis="y", alpha=0.4)
    # st.pyplot(fig1, clear_figure=True)
    fig1.subplots_adjust(bottom=0.15)  # 与图2保持一致的底部留白
    # ---- Equipment breakdown (table + stacked bar chart)
    # st.markdown("### Breakdown by equipment")
    df = pd.DataFrame(res.breakdown, index=hours)
    df.index.name = "hour"


    fig2, ax2 = plt.subplots()
    bottom = np.zeros(24)
    for name, series in df.items():
        ax2.bar(hours, (series.values/1000).round(1), bottom=bottom, label=name)
        bottom += (series.values/1000).round(1)
    ax2.set_xlabel("Hour")
    ax2.set_ylabel("Energy (kWh)")
    ax2.legend(ncol=3, fontsize=8)
    ax2.grid(axis="y", alpha=0.3)
    # st.pyplot(fig2, clear_figure=True)
    ax2.legend(
        ncol=4,  # 每行 4 个图例
        fontsize=8,
        loc="upper center",  # 放在上方中央
        bbox_to_anchor=(0.5, -0.15),  # 调整到底部外侧
        frameon=False
    )
    # fig2.tight_layout(rect=[0, 0.05, 1, 1])  # 给 legend 腾出空间
    fig2.subplots_adjust(bottom=0.28)  # 为底部 legend 预留空间
    st.markdown("### Energy breakdown overview")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Hourly Load Curve**")
        st.pyplot(fig1, clear_figure=True)


    with col2:
        st.markdown("**Equipment Breakdown Chart**")
        st.pyplot(fig2, clear_figure=True)
    st.markdown("**Breakdown Table (Wh)**")
    st.dataframe(df.style.format("{:.1f}"))
else:
    st.info("Fill out the form on the left and click **Run estimation**.")
