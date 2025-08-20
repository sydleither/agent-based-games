"""Compile EGT_HAL final timestep coordinates into processed csvs

Expected usage:
python3 -m data_processing.in_silico.raw_to_processed_ps data_type

Where:
data_type: the name of the directory in data/ containing the raw/ data
"""

import sys
import os
import random

import pandas as pd

from spatial_egt.common import get_data_path


def get_proportion(counts):
    """Calculate proportion resistant at each time step

    :param counts: the sensitive and resistant count
        of a single sample at a single time step
    :type counts: Pandas Series
    :return: proportion resistant at the time step
    :rtype: float
    """
    r_cells = counts.loc[counts["type"] == 1, "x"]
    s_cells = counts.loc[counts["type"] == 0, "x"]
    r_cells = r_cells.iloc[0] if not r_cells.empty else 0
    s_cells = s_cells.iloc[0] if not s_cells.empty else 0
    return r_cells / (r_cells + s_cells)


def get_time_in_range(coords):
    """Get the proportion resistant at each time step"""
    # Get the count of each cell type at each time step
    coords = coords[["time", "type", "x"]]
    counts = coords.groupby(["time", "type"]).count().reset_index()
    # Calculate proportion resistant at each time step
    fr = counts.groupby(["time"])[["type", "x"]]
    fr = fr.apply(get_proportion).reset_index()
    fr = fr[(fr[0] > 0.45) & (fr[0] < 0.55)]
    if len(fr) == 0:
        return None
    time = random.sample(fr["time"].tolist(), 1)[0]
    return time


def main(data_type):
    """Save each raw coordinate file as a processed file"""
    random.seed(42)
    raw_data_path = get_data_path(data_type, "raw")
    processed_data_path = get_data_path(data_type, "processed", 50)
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
                    time = get_time_in_range(df)
                    if time is None:
                        continue
                    df = df[df["time"] == time]
                    df["type"] = df["type"].map(cell_type_map)
                    cols_to_keep = ["type", "x", "y"]
                    df = df[cols_to_keep]
                    df.to_csv(f"{processed_data_path}/{exp_name} {data_dir}.csv", index=False)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Please see the module docstring for usage instructions.")
