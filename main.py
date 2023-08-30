import os
import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(layout="wide")

st.sidebar.markdown("# Enter Finance details")
st.sidebar.markdown("## Initial loan")
starting_loan_rate = st.sidebar.slider(
    "Starting loan rate", min_value=2.0, max_value=10.0, value=6.51, step=0.01
)
starting_tilgung_rate = st.sidebar.slider(
    "Starting payback rate", min_value=0.5, max_value=5.0, value=2.0, step=0.1
)
starting_eigenkapital = st.sidebar.number_input(
    "Starting Eigenkapital",
    min_value=100_000,
    max_value=500_000,
    value=152_000,
    step=1000,
)
starting_loan = st.sidebar.number_input(
    "Starting loan",
    min_value=100_000,
    max_value=500_000,
    value=260_000,
    step=1000,
)
st.sidebar.write("Total cost:", starting_eigenkapital + starting_loan)
remaining_loan = st.sidebar.number_input(
    "Outstanding loan",
    min_value=100_000,
    max_value=500_000,
    value=257_000,
    step=1000,
)

st.sidebar.divider()
st.sidebar.markdown("## Follow-up loan")
months_till_fixing_loan = st.sidebar.number_input(
    "Months until fixing the loan", min_value=0, max_value=12
)
fixed_term = st.sidebar.selectbox("Fixed term", [10, 15, 20])
additional_loan = st.sidebar.number_input(
    "Additional loan",
    min_value=100_000,
    max_value=1_000_000,
    value=320_000,
    step=1000,
)
new_loan_rate = st.sidebar.slider(
    "New loan rate", min_value=1.0, max_value=10.0, value=3.78, step=0.01
)
new_tilgung_rate = st.sidebar.slider(
    "New payback rate", min_value=0.5, max_value=5.0, value=1.0, step=0.1
)
parking = st.sidebar.number_input(
    "Free parking (months)",
    min_value=6,
    max_value=24,
    value=12,
    step=1,
)


def monthly_cost(rate, amount):
    return round(((rate / 100) * amount) / 12, 2)


def calculate_10_year(
    starting_loan_rate,
    remaining_loan,
    starting_tilgung_rate,
    starting_loan,
    parking,
    additional_loan,
    new_loan_rate,
):
    bank_monthly, tilgung_monthly, total_monthly, loan_remaining_monthly = (
        [],
        [],
        [],
        [],
    )
    for month in range(1, 121):
        month_bank, month_tilgung, month_total = 0, 0, 0
        if months_till_fixing_loan > 0 and month <= months_till_fixing_loan:
            month_bank += monthly_cost(starting_loan_rate, remaining_loan)
            month_tilgung += monthly_cost(starting_tilgung_rate, starting_loan)
            month_total += month_bank + month_tilgung
        else:
            if month == parking + 1:
                starting_new_loan = remaining_loan + additional_loan
                remaining_loan += additional_loan
            if month > parking:
                month_tilgung += monthly_cost(new_tilgung_rate, starting_new_loan)
            month_bank += monthly_cost(new_loan_rate, remaining_loan)
            month_total += month_bank + month_tilgung

        remaining_loan -= month_tilgung

        bank_monthly.append(month_bank)
        tilgung_monthly.append(month_tilgung)
        total_monthly.append(month_total)
        loan_remaining_monthly.append(remaining_loan)

    df = pd.DataFrame.from_dict(
        {
            "Bank month (EUR)": bank_monthly,
            "Tilgung month (EUR)": tilgung_monthly,
            "BANK rolling (EUR)": np.cumsum(bank_monthly),
            "TOTAL rolling (EUR)": np.cumsum(total_monthly),
            "Outstanding loan (EUR)": loan_remaining_monthly,
        },
        orient="index",
        columns=[f"month {i}" for i in range(1, 121)],
    )
    fees = pd.DataFrame.from_dict(
        {
            "1 year": sum(bank_monthly[:12]),
            "2 years": sum(bank_monthly[:24]),
            "5 years": sum(bank_monthly[:60]),
            "10 years": sum(bank_monthly[:120]),
        },
        orient="index",
        columns=["fees (EUR)"],
    )
    return df, fees


df, fees = calculate_10_year(
    starting_loan_rate,
    remaining_loan,
    starting_tilgung_rate,
    starting_loan,
    parking,
    additional_loan,
    new_loan_rate,
)
st.markdown("# Loan costs by month")
st.dataframe(df, width=10000)

st.line_chart(
    data=df.T.reset_index(drop=True).loc[
        :, ["BANK rolling (EUR)", "TOTAL rolling (EUR)", "Outstanding loan (EUR)"]
    ]
)

st.divider()
st.markdown("# Cumulative bank costs")
st.dataframe(fees, width=200)
