import csv

import pandas as pd

from spatial_egt.common import get_data_path


def process_spatial_df(df, time):
    df = df[df["Metadata_Timepoint"] == int(time)]
    df = df.rename(columns={"Location_Center_X":"x",
                            "Location_Center_Y":"y"})
    df = df[["x", "y"]]
    df["x"] = df["x"].astype(float).round(0).astype(int)
    df["y"] = df["y"].astype(float).round(0).astype(int)
    return df


def get_spatial_data(data_path, source, plate, well, time):
    folder_name = f"results_stitched_images_plate{plate}"
    spatial_file_name = f"segmentation_results_well_{well}_locations"
    full_path = f"{data_path}/{source}/{folder_name}/{spatial_file_name}"
    s_df = pd.read_csv(f"{full_path}_gfp.csv")
    s_df = process_spatial_df(s_df, time)
    s_df["type"] = "sensitive"
    r_df = pd.read_csv(f"{full_path}_mCherry.csv")
    r_df = process_spatial_df(r_df, time)
    r_df["type"] = "resistant"
    df = pd.concat([s_df, r_df])
    df = df[["type", "x", "y"]]
    return df


def raw_to_processed():
    raw_data_path = get_data_path("in_vitro", "raw")
    processed_data_path = get_data_path("in_vitro", "processed")

    with open(f"{processed_data_path}/payoff.csv") as payoff_csv:
        reader = csv.DictReader(payoff_csv)
        for row in reader:
            source = row["source"]
            sample = row["sample"]
            df = get_spatial_data(raw_data_path, source, row["plate"], row["well"], row["time_id"])
            df.to_csv(f"{processed_data_path}/{source} {sample}.csv", index=False)


if __name__ == "__main__":
    raw_to_processed()