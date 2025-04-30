"""Compile Maxi's preprocessed experimental data into a csv with payoff matrix data"""

import os

import pandas as pd

from spatial_egt.common import calculate_game, get_data_path


def format_raw_df(df, data_source, source, time_to_keep):
    """Format count+payoff raw dataframe for spatial_egt"""
    # Filter to only include desired time and drug concentration
    df = df[df["Time"] == time_to_keep]
    df = df[df["DrugConcentration"] == 0]

    # Calculate game
    df = df.rename({"p11": "a", "p12": "b", "p21": "c", "p22": "d"}, axis=1)
    df["game"] = df.apply(lambda x: calculate_game(x["a"], x["b"], x["c"], x["d"]), axis=1)

    # Add columns for spatial_egt
    df["data_source"] = data_source
    df["source"] = source
    df["sample"] = df["PlateId"].astype(str) + "_" + df["WellId"]
    df["cell_types"] = " ".join(sorted(df["CellType"].unique()))

    # Add initial density (number of cells seeded) column
    df_grp = df[["source", "sample", "Count"]].groupby(["source", "sample"]).sum().reset_index()
    df_grp = df_grp.rename({"Count": "initial_density"}, axis=1)
    df = df.merge(df_grp, on=["source", "sample"])

    # Format and filter columns
    df = df.rename(
        {"WellId": "well", "PlateId": "plate", "SeededProportion_Parental": "initial_fs"}, axis=1
    )
    cols = [
        "data_source",
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


def main(time_to_keep):
    """Combine counts dfs with overview df"""
    raw_data_path = get_data_path("in_vitro", "raw/maxi")
    game_df = pd.read_csv(f"{raw_data_path}/overview_df_spatial_data.csv")

    key = ["ExperimentName", "PlateId", "WellId", "ReplicateId"]
    game_df = game_df[key + ["p11", "p12", "p21", "p22"]]
    game_df["ExperimentName"] = game_df["ExperimentName"].str.lower()

    payoff_df = pd.DataFrame()
    for experiment_name in os.listdir(raw_data_path):
        exp_path = f"{raw_data_path}/{experiment_name}"
        if os.path.isfile(exp_path):
            continue

        # Read in counts file and match to game file
        counts_df = pd.read_csv(f"{exp_path}/{experiment_name}_counts_df_processed.csv")
        counts_df["ExperimentName"] = experiment_name.lower()
        counts_df = counts_df.merge(game_df, on=key)

        # Rank times to match imaging data
        counts_df["time_id"] = counts_df["Time"].rank(method="dense", ascending=True)
        counts_df["time_id"] = counts_df["time_id"].astype(int)

        counts_df = format_raw_df(counts_df, "maxi", experiment_name, time_to_keep)
        payoff_df = pd.concat([payoff_df, counts_df])

    return payoff_df
