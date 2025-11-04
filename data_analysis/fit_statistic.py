import argparse
import os

import numpy as np
import pandas as pd

from spatial_egt.common import get_data_path
from spatial_egt.data_processing.processed_to_statistic import get_statistic_calculation_arguments
from spatial_database import STATISTIC_REGISTRY


def distance(row, stat):
    return np.linalg.norm(row[f"ABM {stat}"] - row[f"Exp {stat}"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-abm_dir", "--abm_data_type", type=str, default="in_silico_fit")
    parser.add_argument("-exp_dir", "--exp_data_type", type=str, default="in_vitro_pc9")
    parser.add_argument("-time", "--time", type=int, default=72)
    parser.add_argument("-stat", "--statistic_name", type=str, default="CPCF_RS")
    args = parser.parse_args()

    stat_path = f"{args.time}/statistics/{args.statistic_name}.pkl"
    df_exp = pd.read_pickle(f"data/{args.exp_data_type}/{stat_path}")
    df_abm = pd.read_pickle(f"data/{args.abm_data_type}/{stat_path}")

    df_abm["params"] = df_abm["sample"].str.split("-").str[1]
    df_abm["Expansion"] = df_abm["params"].str.split("_").str[0]
    df_abm["Interaction"] = df_abm["params"].str.split("_").str[1]
    df_abm["Reproduction"] = df_abm["params"].str.split("_").str[2]

    df_abm[f"ABM {args.statistic_name}"] = df_abm[args.statistic_name]
    df_exp[f"Exp {args.statistic_name}"] = df_exp[args.statistic_name]
    df = df_abm.merge(df_exp, on=["source", "sample"])
    df["distance"] = df.apply(distance, args=(args.statistic_name,))

    print(df[["params", "distance"]].groupby("params").mean().sort_values(by="distance"))
    print(df[["params", "source", "distance"]].groupby(["params", "source"]).mean().sort_values(by="distance"))


if __name__ == "__main__":
    main()
