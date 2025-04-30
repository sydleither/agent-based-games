"""Compile Jinling's experimental data into a csv with payoff matrix data

A majority of this code is modified from Maxi's example game assay analysis.
"""

from itertools import product

import pandas as pd

from spatial_egt.common import get_data_path
from data_processing.in_vitro.maxi.raw_to_processed_payoff import format_raw_df
from data_processing.in_vitro.jinling.game_analysis_utils import (
    estimate_game_parameters,
    estimate_growth_rate,
    compute_population_fraction,
)


def calculate_payoffs(growth_rate_df, cell_type_list):
    """Payoff df from Maxi's pipeline"""
    tmp_list = []
    for drug_concentration in growth_rate_df["DrugConcentration"].unique():
        curr_data_df = growth_rate_df[(growth_rate_df["DrugConcentration"] == drug_concentration)]
        game_params_dict = estimate_game_parameters(
            growth_rate_df=curr_data_df,
            fraction_col="Fraction_Sensitive",
            growth_rate_col="GrowthRate",
            cell_type_col="CellType",
            cell_type_list=cell_type_list,
            method="theil",
            ci=0.95,
        )
        tmp_list.append(
            {
                "DrugConcentration": float(drug_concentration),
                "Type1": cell_type_list[0],
                "Type2": cell_type_list[1],
                **game_params_dict,
            }
        )
    game_params_df = pd.DataFrame(tmp_list)
    return game_params_df


def calculate_growth_rates(counts_df, growth_rate_window, cell_type_list):
    """Growth rates for Maxi's pipeline"""
    metadata_columns = [
        col
        for col in counts_df.columns
        if col not in ["Time", "Count", "ImageId", "CellType", "WellId", "PlateId"]
    ]
    tmp_list = []
    for plate_id, well_id, cell_type in product(
        counts_df["PlateId"].unique(), counts_df["WellId"].unique(), cell_type_list
    ):
        slope, intercept, low_slope, high_slope = estimate_growth_rate(
            data_df=counts_df[counts_df["PlateId"] == plate_id],
            well_id=well_id,
            cell_type=cell_type,
            growth_rate_window=growth_rate_window,
            count_threshold=10,
        )
        fractions_dict = compute_population_fraction(
            counts_df[counts_df["PlateId"] == plate_id],
            well_id=well_id,
            fraction_window=growth_rate_window,
            n_images="all",
            cell_type_list=cell_type_list,
        )
        curr_df = counts_df[
            (counts_df["PlateId"] == plate_id)
            & (counts_df["WellId"] == well_id)
            & (counts_df["CellType"] == cell_type)
        ]
        tmp_list.append(
            {
                "PlateId": plate_id,
                "WellId": well_id,
                "CellType": cell_type,
                **fractions_dict,
                **curr_df[metadata_columns].iloc[0].to_dict(),
                "GrowthRate": slope,
                "GrowthRate_lowerBound": low_slope,
                "GrowthRate_higherBound": high_slope,
                "Intercept": intercept,
                "GrowthRate_normalised": slope,
                "GrowthRate_lowerBound_normalised": low_slope,
                "GrowthRate_higherBound_normalised": high_slope,
            }
        )
    growth_rate_df = pd.DataFrame(tmp_list)
    return growth_rate_df


def main(time_to_keep):
    """Process count data"""
    raw_data_path = get_data_path("in_vitro", "raw/jinling")
    counts_df = pd.read_csv(f"{raw_data_path}/count_data.csv")

    growth_rate_window = [24, 72]
    cell_types = ["Sensitive", "Resistant"]
    growth_rate_df = calculate_growth_rates(counts_df, growth_rate_window, cell_types)
    payoff_df = calculate_payoffs(growth_rate_df, cell_types)
    df = payoff_df.merge(counts_df, on="DrugConcentration")
    df["time_id"] = f"{(time_to_keep // 24):02}d00h00m"
    df = format_raw_df(df, "jinling", "jinling", time_to_keep)

    return df
