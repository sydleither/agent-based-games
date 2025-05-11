"""Compile Jinling's experimental spatial data into formatted csvs

The payoff matrix data (labels.csv) should already be saved

Expected usage:
python3 -m data_processing.in_vitro.h358.raw_to_processed_spatial
"""

import csv

import pandas as pd

from spatial_egt.common import get_data_path


def stitch_coordinates(raw_data_path, source, well, time):
    """Coordinates are split into four quadrants- stitch them back together"""
    df = pd.DataFrame()
    for i in range(1, 5):
        file_name = f"csv_{well}_{i}_{time}.csv"
        df_i = pd.read_csv(f"{raw_data_path}/{source}/{file_name}")
        df_i["part"] = i
        df = pd.concat([df_i, df])
    df = df.reset_index()
    width = df["x"].max()
    height = df["y"].max()
    df.loc[df["part"] == 2, "x"] = df["x"] + width
    df.loc[df["part"] == 3, "y"] = df["y"] + height
    df.loc[df["part"] == 4, "x"] = df["x"] + width
    df.loc[df["part"] == 4, "y"] = df["y"] + height
    return df


def main():
    """Get coordinates of each sample in labels.csv"""
    data_dir = "in_vitro_h358"
    raw_data_path = get_data_path(data_dir, "raw")
    payoff_data_path = get_data_path(data_dir, ".")
    processed_data_path = get_data_path(data_dir, "processed")

    with open(f"{payoff_data_path}/labels.csv", encoding="UTF-8") as payoff_csv:
        reader = csv.DictReader(payoff_csv)
        for row in reader:
            source = row["source"]
            sample = row["sample"]
            well = row["well"]
            time = row["time_id"]
            df = stitch_coordinates(raw_data_path, source, well, time)
            df = df[["x", "y", "CellType"]]
            df = df.rename({"CellType": "type"}, axis=1)
            df["type"] = df["type"].map({"gfp":"sensitive", "mcherry":"resistant"})
            df.to_csv(f"{processed_data_path}/{source} {sample}.csv", index=False)


if __name__ == "__main__":
    main()
