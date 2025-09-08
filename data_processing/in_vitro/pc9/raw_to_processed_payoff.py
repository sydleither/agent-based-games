"""Compile Dag's experimental data into a csv with payoff matrix data"""

import argparse
import os

import pandas as pd

from data_processing.in_vitro.game_analysis_utils import calculate_growth_rates, calculate_payoffs
from spatial_egt.common import calculate_game, get_data_path


def format_raw_df(df, source, sensitive_type, time_to_keep):
    """Format count+payoff raw dataframe for spatial_egt"""
    # Add initial density column (number of initial cells divided by max number of cells seen)
    df_grp = df[["PlateId", "WellId", "Time", "Count"]].groupby(["PlateId", "WellId", "Time"]).sum()
    df_grp = df_grp.reset_index()
    df_grp = df_grp.rename({"Count": "Sum_Count"}, axis=1)
    df = df.merge(df_grp, on=["PlateId", "WellId", "Time"])
    df = df[df["CellType"] == sensitive_type].drop_duplicates()
    df["Density"] = df["Sum_Count"] / df["Sum_Count"].max()
    df_0 = df[df["Time"] == 0][["PlateId", "WellId", "Density"]]
    df_0 = df_0.rename({"Density": "initial_density"}, axis=1)
    df = df.merge(df_0, on=["PlateId", "WellId"], how="left")

    # Filter to only include desired time
    df = df[df["Time"] == time_to_keep]

    # Calculate game
    df = df.rename({"p11": "a", "p12": "b", "p21": "c", "p22": "d"}, axis=1)
    df["game"] = df.apply(lambda x: calculate_game(x["a"], x["b"], x["c"], x["d"]), axis=1)

    # Add columns for spatial_egt
    df["source"] = source
    df["sample"] = df["PlateId"].astype(str) + "_" + df["WellId"]
    df["cell_types"] = df["Type1"] + " " + df["Type2"]

    # Format and filter columns
    df = df.rename(
        {"WellId": "well", "PlateId": "plate", "Frequency": "initial_fs"}, axis=1
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
    return df


def main():
    """Process count data for each experiment"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_dir", type=str, default="in_vitro_pc9")
    parser.add_argument("-start", "--growth_rate_start", type=int, default=24)
    parser.add_argument("-end", "--growth_rate_end", type=int, default=72)
    parser.add_argument("-time", "--time_to_keep", type=int, default=72)
    args = parser.parse_args()

    raw_data_path = get_data_path(args.data_dir, "raw")
    growth_rate_window = [args.growth_rate_start, args.growth_rate_end]

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
        df_exp = format_raw_df(df_exp, experiment_name, cell_types[0], args.time_to_keep)
        df = pd.concat([df, df_exp])
    data_path = get_data_path(args.data_dir, ".")
    df.to_csv(f"{data_path}/labels.csv", index=False)


if __name__ == "__main__":
    main()
