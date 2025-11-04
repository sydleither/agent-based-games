import argparse
import json
import os

import pandas as pd

from spatial_egt.common import get_data_path


def main():
    """Save each raw coordinate file as a processed file"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_silico")
    parser.add_argument("-time", "--time", type=int, default=None)
    args = parser.parse_args()

    raw_data_path = get_data_path(args.data_type, "raw")
    processed_data_path = get_data_path(args.data_type, "processed", args.time)
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
                    if args.time is None:
                        df = df[df["time"] == df["time"].max()]
                    else:
                        df = df[df["time"] == args.time]
                    df["type"] = df["type"].map(cell_type_map)
                    config = json.load(open(f"{data_path}/{data_dir}.json", encoding="UTF-8"))
                    df["x"] = df["x"] * config.get("grid_expansion", 1)
                    df["y"] = df["y"] * config.get("grid_expansion", 1)
                    df = df[["type", "x", "y"]]
                    df.to_csv(f"{processed_data_path}/{exp_name} {data_dir}.csv", index=False)


if __name__ == "__main__":
    main()
