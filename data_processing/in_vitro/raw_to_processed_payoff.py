import os

import pandas as pd

from spatial_egt.common import calculate_game, get_data_path


def main():
    raw_data_path = get_data_path("in_vitro", "raw")
    processed_data_path = get_data_path("in_vitro", "processed")
    game_df = pd.read_csv(f"{raw_data_path}/overview_df_spatial_data.csv")

    key = ["ExperimentName", "PlateId", "WellId", "ReplicateId"]
    game_df = game_df[key+["p11", "p12", "p21", "p22"]]
    game_df = game_df.rename({"p11":"a", "p12":"b", "p21":"c", "p22":"d"}, axis=1)
    game_df["ExperimentName"] = game_df["ExperimentName"].str.lower()

    time_to_keep = 24
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
        counts_df = counts_df[["WellId", "PlateId", "time_id",
                               "a", "b", "c", "d", "game"]]
        counts_df = counts_df.drop_duplicates()
        counts_df["source"] = experiment_name
        counts_df["sample"] = counts_df["PlateId"].astype(str)+"_"+counts_df["WellId"]

        # Rename and reorder columns
        counts_df = counts_df.rename({"WellId":"well", "PlateId":"plate"}, axis=1)
        counts_df = counts_df[["source", "sample", "plate", "well", "time_id",
                               "a", "b", "c", "d", "game"]]

        payoff_df = pd.concat([payoff_df, counts_df])

    payoff_df.to_csv(f"{processed_data_path}/payoff.csv", index=False)


if __name__ == "__main__":
    main()