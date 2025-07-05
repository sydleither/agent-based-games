"""Split ABM grid into multiple samples

Expected usage:
python3 -m data_processing.in_silico.drug_gradient data_type grid_size

Where:
data_type: the name of the directory in data/ containing the raw/ data
grid_size: the resulting size the split grids should be
"""

import json
import os
import sys

import pandas as pd

from spatial_egt.common import get_data_path


def save_splits(data_path, data_dir, rep, config, df, grid_size):
    config["x"] = grid_size
    config["y"] = grid_size
    for split in df["split"].unique():
        df_split = df[df["split"] == split]
        drug_concentration = df_split["drug"].values[0]
        split_config = config.copy()
        split_config["A"] = split_config["A"]*(1-drug_concentration)
        split_config["B"] = split_config["B"]*(1-drug_concentration)
        os.makedirs(f"{data_path}/{data_dir}/{rep}_{split}/{rep}")
        with open(f"{data_path}/{data_dir}/{rep}_{split}/{rep}_{split}.json", "w") as f:
            json.dump(split_config, f)
        df_split.to_csv(f"{data_path}/{data_dir}/{rep}_{split}/{rep}/2Dcoords.csv", index=False)


def assign_splits(row, num_splits, grid_size):
    for i in range(num_splits):
        for j in range(num_splits):
            x_in_bounds = (i*grid_size <= row["x"] < (i+1)*grid_size)
            y_in_bounds = (j*grid_size <= row["y"] < (j+1)*grid_size)
            if x_in_bounds and y_in_bounds:
                row["split"] = f"{i}_{j}"
                row["x"] = row["x"] - i*grid_size
                row["y"] = row["y"] - j*grid_size
                return row
    print(row)
    raise ValueError("Coordinates unable to be properly split.")


def main(data_type, grid_size):
    """Extract and compile game data from each EGT_HAL config"""
    curr_data_path = get_data_path(data_type, "raw")
    new_data_path = get_data_path(data_type+"_split", "raw")
    for exp_name in os.listdir(curr_data_path):
        exp_path = f"{curr_data_path}/{exp_name}"
        if os.path.isfile(exp_path):
            continue
        for data_dir in os.listdir(exp_path):
            data_path = f"{exp_path}/{data_dir}"
            if os.path.isfile(data_path):
                continue
            config = json.load(open(f"{data_path}/{data_dir}.json", encoding="UTF-8"))
            num_splits = config["x"] // grid_size
            for rep_dir in os.listdir(data_path):
                rep_path = f"{data_path}/{rep_dir}"
                if os.path.isfile(rep_path):
                    continue
                for model_file in os.listdir(rep_path):
                    model_path = f"{rep_path}/{model_file}"
                    if not model_file.endswith("coords.csv"):
                        continue
                    if not os.path.exists(model_path) or os.path.getsize(model_path) == 0:
                        print(f"Data not found in {model_path}")
                        continue
                    df = pd.read_csv(model_path)
                    df = df[df["time"] == df["time"].max()]
                    df = df.apply(assign_splits, args=(num_splits, grid_size), axis=1)
                    save_splits(new_data_path, data_dir, rep_dir, config, df, grid_size)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], int(sys.argv[2]))
    else:
        print("Please see the module docstring for usage instructions.")
