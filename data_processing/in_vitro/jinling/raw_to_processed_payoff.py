"""Compile Jinling's experimental data into a csv with payoff matrix data"""

import pandas as pd

from spatial_egt.common import get_data_path
from data_processing.in_vitro.maxi.raw_to_processed_payoff import format_raw_df
from data_processing.in_vitro.game_analysis_utils import calculate_growth_rates, calculate_payoffs


def main(time_to_keep):
    """Process count data"""
    raw_data_path = get_data_path("in_vitro", "raw/jinling")
    counts_df = pd.read_csv(f"{raw_data_path}/count_data.csv")

    growth_rate_window = [24, 72]
    cell_types = ["Sensitive", "Resistant"]
    growth_rate_df = calculate_growth_rates(counts_df, growth_rate_window, cell_types)
    payoff_df = calculate_payoffs(growth_rate_df, cell_types, "Fraction_Sensitive")
    df = payoff_df.merge(counts_df, on="DrugConcentration")
    df["time_id"] = f"{(time_to_keep // 24):02}d00h00m"
    df = format_raw_df(df, "jinling", "jinling", time_to_keep)

    return df
