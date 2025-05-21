"""Compile Jinling's experimental data into a csv with payoff matrix data"""

import pandas as pd

from spatial_egt.common import get_data_path
from data_processing.in_vitro.pc9.raw_to_processed_payoff import format_raw_df
from data_processing.in_vitro.game_analysis_utils import calculate_growth_rates, calculate_payoffs


def main():
    """Process count data"""
    data_dir = "in_vitro_h358"
    raw_data_path = get_data_path(data_dir, "raw")
    growth_rate_window = [24, 72]
    time_to_keep = 72

    counts_df = pd.read_csv(f"{raw_data_path}/count_data.csv")
    counts_df = counts_df[counts_df["DrugConcentration"] == 0]
    cell_types = ["Sensitive", "Resistant"]
    growth_rate_df = calculate_growth_rates(counts_df, growth_rate_window, cell_types)
    payoff_df = calculate_payoffs(growth_rate_df, cell_types, "Fraction_Sensitive")
    df = payoff_df.merge(counts_df, on="DrugConcentration")
    df["time_id"] = f"{(time_to_keep // 24):02}d00h00m"
    df = format_raw_df(df, "R2", cell_types[0], time_to_keep)
    data_path = get_data_path(data_dir, ".")
    df.to_csv(f"{data_path}/labels.csv", index=False)


if __name__ == "__main__":
    main()
