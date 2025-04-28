"""Compile Jinling's experimental spatial data into formatted csvs

The payoff matrix data (labels.csv) should already be saved

Expected usage:
python3 -m data_processing.in_vitro.jinling.raw_to_processed_spatial
"""

import csv

import pandas as pd

from spatial_egt.common import get_data_path


def main():
    """Get coordinates of each sample in labels.csv"""
    raw_data_path = get_data_path("in_vitro", "raw/jinling")
    payoff_data_path = get_data_path("in_vitro", ".")
    processed_data_path = get_data_path("in_vitro", "processed")

    with open(f"{payoff_data_path}/labels.csv", encoding="UTF-8") as payoff_csv:
        reader = csv.DictReader(payoff_csv)
        for row in reader:
            if row["data_source"] != "jinling":
                continue
            source = row["source"]
            sample = row["sample"]
            well = row["well"]
            plate = row["plate"]
            time = row["time_id"]
            df = pd.read_csv(f"{raw_data_path}/coordinates/csv_{well}_{plate}_{time}.csv")
            df = df[["x", "y", "CellType"]]
            df = df.rename({"CellType": "type"}, axis=1)
            df["type"] = df["type"].map({"gfp":"sensitive", "mcherry":"resistant"})
            df.to_csv(f"{processed_data_path}/{source} {sample}.csv", index=False)


if __name__ == "__main__":
    main()
