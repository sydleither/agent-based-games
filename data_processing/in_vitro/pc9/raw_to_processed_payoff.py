"""Compile Dag's experimental data into a csv with payoff matrix data"""

import os

import pandas as pd

from data_processing.in_vitro.game_analysis_utils import calculate_growth_rates, calculate_payoffs
from spatial_egt.common import calculate_game, get_data_path


def format_raw_df(df, source, time_to_keep):
    """Format count+payoff raw dataframe for spatial_egt"""
    # Add initial density (number of cells seeded) column
    df_0 = df[df["Time"] == 0]
    df_grp = df_0[["PlateId", "WellId", "Count"]].groupby(["PlateId", "WellId"]).sum().reset_index()
    df_grp = df_grp.rename({"Count": "initial_density"}, axis=1)
    df = df.merge(df_grp, on=["PlateId", "WellId"])

    # Filter to only include desired time
    df = df[df["Time"] == time_to_keep]

    # Calculate game
    df = df.rename({"p11": "a", "p12": "b", "p21": "c", "p22": "d"}, axis=1)
    df["game"] = df.apply(lambda x: calculate_game(x["a"], x["b"], x["c"], x["d"]), axis=1)

    # Add columns for spatial_egt
    df["source"] = source
    df["sample"] = df["PlateId"].astype(str) + "_" + df["WellId"]
    df["cell_types"] = " ".join(sorted(df["CellType"].unique()))

    # Format and filter columns
    df = df.rename(
        {"WellId": "well", "PlateId": "plate", "SeededProportion_Parental": "initial_fs"}, axis=1
    )
    cols = [
        "source",
        "sample",
        "plate",
        "well",
        "time_id",
        "cell_types",
        "initial_fs",
        "initial_density",
        "a",
        "b",
        "c",
        "d",
        "game",
    ]
    df = df[cols]
    df = df.drop_duplicates()
    return df


def main():
    """Process count data for each experiment"""
    data_dir = "in_vitro_pc9"
    raw_data_path = get_data_path(data_dir, "raw")
    growth_rate_window = [24, 72]
    time_to_keep = 72

    df = pd.DataFrame()
    for experiment_name in os.listdir(raw_data_path):
        exp_path = f"{raw_data_path}/{experiment_name}"
        if os.path.isfile(exp_path):
            continue
        counts_df = pd.read_csv(f"{exp_path}/{experiment_name}_counts_df_processed.csv")
        counts_df = counts_df[counts_df["DrugConcentration"] == 0]
        raw_cell_types = counts_df["CellType"].unique()
        cell_types = [0, 1]
        cell_types[0] = [x for x in raw_cell_types if "gfp" in x][0]
        cell_types[1] = [x for x in raw_cell_types if "mcherry" in x][0]
        growth_rate_df = calculate_growth_rates(counts_df, growth_rate_window, cell_types)
        payoff_df = calculate_payoffs(growth_rate_df, cell_types, "SeededProportion_Parental")
        df_exp = payoff_df.merge(counts_df, on="DrugConcentration")
        df_exp["time_id"] = df_exp["Time"].rank(method="dense", ascending=True)
        df_exp["time_id"] = df_exp["time_id"].astype(int)
        df_exp = format_raw_df(df_exp, experiment_name, time_to_keep)
        df = pd.concat([df, df_exp])
    data_path = get_data_path(data_dir, ".")
    df.to_csv(f"{data_path}/labels.csv", index=False)


if __name__ == "__main__":
    main()
