import argparse
import json
import os

import pandas as pd

from spatial_egt.common import calculate_game, get_data_path


def main():
    """Extract and compile game data from each EGT_HAL config"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_silico")
    args = parser.parse_args()

    raw_data_path = get_data_path(args.data_type, "raw")
    df_entries = []
    for experiment_name in os.listdir(raw_data_path):
        experiment_path = f"{raw_data_path}/{experiment_name}"
        if os.path.isfile(experiment_path):
            continue
        for data_dir in os.listdir(experiment_path):
            data_path = f"{experiment_path}/{data_dir}"
            if os.path.isfile(data_path):
                continue
            df_row = {}
            config = json.load(open(f"{data_path}/{data_dir}.json", encoding="UTF-8"))
            df_row["source"] = experiment_name
            df_row["sample"] = data_dir
            df_row["initial_density"] = config["numCells"] / (config["x"] * config["y"])
            df_row["initial_fs"] = 1 - config["proportionResistant"]
            df_row["a"] = config["A"]
            df_row["b"] = config["B"]
            df_row["c"] = config["C"]
            df_row["d"] = config["D"]
            df_row["game"] = calculate_game(config["A"], config["B"], config["C"], config["D"])
            df_entries.append(df_row)
    data_path = get_data_path(args.data_type, ".")
    df = pd.DataFrame(data=df_entries)
    df = df[df["game"] != "Unknown"]
    df.to_csv(f"{data_path}/labels.csv", index=False)


if __name__ == "__main__":
    main()
