"""Compile EGT_HAL final timestep coordinates into processed csvs

Expected usage:
python3 -m data_processing.in_silico.raw_to_processed_spatial data_type

Where:
data_type: the name of the directory in data/ containing the raw/ data
"""

import sys
import os

import pandas as pd

from spatial_egt.common import get_data_path


def main(data_type):
    """Save each raw coordinate file as a processed file"""
    raw_data_path = get_data_path(data_type, "raw")
    processed_data_path = get_data_path(data_type, "processed")
    cell_type_map = {0: "sensitive", 1: "resistant"}
    for exp_name in os.listdir(raw_data_path):
        exp_path = f"{raw_data_path}/{exp_name}"
        if os.path.isfile(exp_path):
            continue
        for data_dir in os.listdir(exp_path):
            data_path = f"{exp_path}/{data_dir}"
            if os.path.isfile(data_path):
                continue
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
                    df["type"] = df["type"].map(cell_type_map)
                    cols_to_keep = ["type", "x", "y"]
                    df = df[cols_to_keep]
                    df.to_csv(f"{processed_data_path}/{exp_name} {data_dir}.csv", index=False)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Please see the module docstring for usage instructions.")
