import pandas as pd
import streamlit as st
from src.config import MONTHS_TILL_FIXING, REMAIN_AFTER_PARKING
from src.dataHandler import calculate_10_year

# app config
st.set_page_config(layout="wide")


######################################
############ SIDEBAR TOP #############
######################################

st.sidebar.markdown("# Project Finance Details")
st.sidebar.markdown("## Initial Loan")
starting_personal = st.sidebar.number_input(
    "Starting personal contribution (EUR)",
    min_value=100_000,
    max_value=500_000,
    value=152_000,
    step=1000,
)
starting_loan = st.sidebar.number_input(
    "Starting loan (EUR)",
    min_value=100_000,
    max_value=500_000,
    value=260_000,
    step=1000,
)
st.sidebar.write("TOTAL Initial Cost (EUR):", starting_personal + starting_loan)
remaining_loan = st.sidebar.number_input(
    "Outstanding loan at new financing (EUR)",
    min_value=100_000,
    max_value=500_000,
    value=257_000,
    step=1000,
)
starting_loan_rate = st.sidebar.slider(
    "Starting loan rate (%)", min_value=2.0, max_value=10.0, value=6.51, step=0.01
)
starting_tilgung_rate = st.sidebar.slider(
    "Starting payback rate (%)", min_value=0.5, max_value=5.0, value=2.0, step=0.1
)
st.sidebar.divider()

######################################
########## SIDEBAR BOTTOM ############
######################################

st.sidebar.markdown("## Follow-up Loan")
additional_loan = st.sidebar.number_input(
    "Additional loan (EUR)",
    min_value=1_000,
    max_value=1_000_000,
    value=320_000,
    step=1000,
)
st.sidebar.write("TOTAL LOAN (EUR):", starting_loan + additional_loan)
additional_personal = st.sidebar.number_input(
    "Additional personal contributions (EUR)",
    min_value=1_000,
    max_value=1_000_000,
    value=80_000,
    step=1000,
)

parking = st.sidebar.number_input(
    "Free parking (months)",
    min_value=6,
    max_value=24,
    value=12,
    step=1,
)

new_loan_rate = st.sidebar.slider(
    "New loan rate (%)", min_value=1.0, max_value=10.0, value=3.78, step=0.01
)
new_tilgung_rate = st.sidebar.slider(
    "New payback rate (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.1
)
st.sidebar.markdown("## Build Project Details")
months_first_project_payment = st.sidebar.slider(
    "Expected first project payment (months from now)",
    min_value=1,
    max_value=24,
    value=6,
)
max_months_last_project_payment = st.sidebar.slider(
    "Worst-case last project payment (months from now)",
    min_value=months_first_project_payment,
    max_value=48,
    value=18,
)

######################################
############# MAIN PAGE ##############
######################################

with st.spinner():
    grid_search = {}
    for fix in MONTHS_TILL_FIXING:
        grid_search[fix] = {}
        for scenario in REMAIN_AFTER_PARKING:
            scenario_marker = ";".join(map(str, scenario))
            df, fees = calculate_10_year(
                fix,
                starting_loan_rate,
                remaining_loan,
                starting_tilgung_rate,
                starting_loan,
                parking,
                additional_loan,
                new_loan_rate,
                remaining_after_parking=scenario,
            )
            grid_search[fix][scenario_marker] = {
                "fees": fees,
                "details": df,
            }
    lst = []
    for key, item in grid_search.items():
        lst.extend(
            [
                (key, k, data["fees"].loc["10 years", "fees (EUR)"])
                for k, data in item.items()
            ]
        )
    comparison = pd.DataFrame(
        sorted(lst, key=lambda x: x[2]),
        columns=[
            "Months till fix",
            "Post-parking remaning loan",
            "fees after 10 years (EUR)",
        ],
    )

st.markdown("# Cheapest Fee Scenarios")
st.dataframe(comparison, hide_index=True)

cheapest = grid_search[comparison.loc[0, "Months till fix"]][
    comparison.loc[0, "Post-parking remaning loan"]
]

st.markdown("# Cheapest Loan scenario by month")
st.dataframe(
    cheapest["details"],
    width=10000,
)

st.line_chart(
    data=cheapest["details"]
    .T.reset_index(drop=True)
    .loc[:, ["BANK rolling (EUR)", "TOTAL rolling (EUR)", "Outstanding loan (EUR)"]]
)

st.divider()
st.markdown("# Cumulative bank costs")
st.dataframe(cheapest["fees"], width=200)
