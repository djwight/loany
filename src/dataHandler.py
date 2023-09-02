import pandas as pd
import numpy as np
from src.config import PARKING_FEE


def monthly_cost(rate, amount):
    return round(((rate / 100) * amount) / 12, 2)


def calculate_10_year(
    months_till_fixing_loan,
    starting_loan_rate,
    remaining_loan,
    starting_tilgung_rate,
    starting_loan,
    parking,
    additional_loan,
    new_loan_rate,
    remaining_after_parking,
):
    bank_monthly, tilgung_monthly, total_monthly, loan_remaining_monthly = (
        [],
        [],
        [],
        [],
    )
    for month in range(1, 121):
        month_bank, month_tilgung, month_total = 0, 0, 0
        # old loan only
        if months_till_fixing_loan > 0 and month <= months_till_fixing_loan:
            month_bank += monthly_cost(starting_loan_rate, remaining_loan)
            month_tilgung += monthly_cost(starting_tilgung_rate, starting_loan)
            month_total += month_bank + month_tilgung
        else:
            if month == parking + 1:
                starting_new_loan = remaining_loan + additional_loan
                remaining_loan += additional_loan
            if month > parking and len(remaining_after_parking) == 0:
                month_tilgung += monthly_cost(new_loan_rate, starting_new_loan)
            elif len(remaining_after_parking) != 0:
                month_bank += monthly_cost(PARKING_FEE, remaining_after_parking[0])
                remaining_after_parking.pop(0)
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
