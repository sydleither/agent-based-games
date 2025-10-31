import argparse
import os

import numpy as np
import pandas as pd

from spatial_egt.common import get_data_path
from spatial_egt.data_processing.processed_to_statistic import get_statistic_calculation_arguments
from spatial_database import STATISTIC_REGISTRY


def get_stat(row, raw_data_path, time, stat_name, stat_calculation, stat_args):
    cell_type_map = {0: "sensitive", 1: "resistant"}
    source = row["source"]
    sample = row["sample"]
    stats = []
    for seed in os.listdir(f"{raw_data_path}/{source}/{sample}"):
        path = f"{raw_data_path}/{source}/{sample}/{seed}/2Dcoords.csv"
        if not os.path.isfile(path):
            continue
        coords = pd.read_csv(path)
        coords["type"] = coords["type"].map(cell_type_map)
        coords = coords[coords["time"] == time]
        coords["x"] = coords["x"] * int(row["expansion"])
        coords["y"] = coords["y"] * int(row["expansion"])
        statistic = stat_calculation(coords, **stat_args)
        if isinstance(statistic, list) or isinstance(statistic, np.ndarray):
            if stat_calculation.__name__.endswith("dist"):
                stats.append(np.mean(statistic))
            else:
                stats.append(np.min(statistic))
        else:
            stats.append(statistic)
    row[stat_name] = np.mean(stats)
    return row


def read_abm_data(data_type, stat_name, time, source, sample_id):
    # Get file names
    raw_data_path = get_data_path(data_type, "raw")
    data_path = get_data_path(data_type, ".")
    df = pd.read_csv(f"{data_path}/labels.csv")
    df["sample_id"] = df["sample"].str.split("-").str[0]
    if source is not None:
        df = df[(df["source"] == source)]
    if sample_id is not None:
        df = df[(df["sample_id"] == sample_id)]
    df["expansion"] = df["sample"].str.split("-").str[1]
    df["interaction"] = df["sample"].str.split("-").str[2]
    df["reproduction"] = df["sample"].str.split("-").str[3]

    # Get statistic parameters
    stat_calculation = STATISTIC_REGISTRY[stat_name]
    stat_args = get_statistic_calculation_arguments(data_type, stat_name)

    # Save statistic for each run
    df_abm = df.apply(
        get_stat,
        axis=1,
        args=(
            raw_data_path,
            time,
            stat_name,
            stat_calculation,
            stat_args,
        ),
    )
    df_abm["sample"] = df_abm["sample_id"]
    return df_abm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-abm_dir", "--abm_data_type", type=str, default="in_silico_fit")
    parser.add_argument("-exp_dir", "--exp_data_type", type=str, default="in_vitro_pc9")
    parser.add_argument("-time", "--time", type=int, default=72)
    parser.add_argument("-stat", "--statistic_name", type=str, default="CPCF_RS")
    parser.add_argument("-src", "--source", type=str, default=None)
    parser.add_argument("-sam", "--sample", type=str, default=None)
    args = parser.parse_args()

    abm_cpcf_file = f"{get_data_path(args.abm_data_type, '.')}/{args.statistic_name}.pkl"
    if not os.path.isfile(abm_cpcf_file):
        df_abm = read_abm_data(
            args.abm_data_type,
            args.statistic_name,
            args.time,
            args.source,
            args.sample,
        )
        df_abm.to_pickle(abm_cpcf_file)
    else:
        df_abm = pd.read_csv(abm_cpcf_file)

    df_exp = pd.read_pickle(
        f"data/{args.exp_data_type}/{args.time}/statistics/{args.statistic_name}.pkl"
    )
    df_exp[args.statistic_name] = np.min(df_exp[args.statistic_name])

    df_abm[f"ABM {args.statistic_name}"] = df_abm[args.statistic_name]
    df_exp[f"Exp {args.statistic_name}"] = df_exp[args.statistic_name]
    df = df_abm.merge(df_exp, on=["source", "sample"])
    df["distance"] = df[f"Exp {args.statistic_name}"] - df[f"ABM {args.statistic_name}"]
    print(df)

    print(df[["sample", "distance"]].groupby("sample").mean().sort_values())
    print(df[["source", "distance"]].groupby("source").mean().sort_values())


if __name__ == "__main__":
    main()
