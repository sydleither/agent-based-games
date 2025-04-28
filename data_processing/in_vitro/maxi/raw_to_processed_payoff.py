"""Compile Maxi's preprocessed experimental data into a csv with payoff matrix data"""

import os

import pandas as pd

from spatial_egt.common import calculate_game, get_data_path


def main(time_to_keep):
    """Combine counts dfs with overview df"""
    raw_data_path = get_data_path("in_vitro", "raw/maxi")
    game_df = pd.read_csv(f"{raw_data_path}/overview_df_spatial_data.csv")

    key = ["ExperimentName", "PlateId", "WellId", "ReplicateId"]
    game_df = game_df[key + ["p11", "p12", "p21", "p22"]]
    game_df = game_df.rename({"p11": "a", "p12": "b", "p21": "c", "p22": "d"}, axis=1)
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

        # Rank times to match imaging data, then filter to only hold one time point
        counts_df["time_id"] = counts_df["Time"].rank(method="dense", ascending=True)
        counts_df["time_id"] = counts_df["time_id"].astype(int)
        counts_df = counts_df[counts_df["Time"] == time_to_keep]

        # Calculate game
        counts_df["game"] = counts_df.apply(
            lambda x: calculate_game(x["a"], x["b"], x["c"], x["d"]), axis=1
        )

        # Filter to only contain wells with no drug
        counts_df = counts_df[counts_df["DrugConcentration"] == 0]

        # Only keep relevant columns
        cell_types = " ".join(sorted(counts_df["CellType"].unique()))
        counts_df = counts_df[["WellId", "PlateId", "time_id", "a", "b", "c", "d", "game"]]
        counts_df = counts_df.drop_duplicates()
        counts_df["data_source"] = "maxi"
        counts_df["source"] = experiment_name
        counts_df["sample"] = counts_df["PlateId"].astype(str) + "_" + counts_df["WellId"]
        counts_df["cell_types"] = cell_types

        # Rename and reorder columns
        counts_df = counts_df.rename({"WellId": "well", "PlateId": "plate"}, axis=1)
        cols = [
            "data_source",
            "source",
            "sample",
            "plate",
            "well",
            "time_id",
            "cell_types",
            "a",
            "b",
            "c",
            "d",
            "game"
        ]
        counts_df = counts_df[cols]
        payoff_df = pd.concat([payoff_df, counts_df])

    return payoff_df
