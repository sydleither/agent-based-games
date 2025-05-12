"""Fit ABM interaction and reproduction radii to experiment count data.

Expected usage: python3 -m data_analysis.fit_experimental data_type (source) (sample_id)

Where:
data_type: the name of the directory in data/ containing raw/ ABM data
source: optional, the name of the source of the data
sample_id: optional, a sample_id to visualize the fits on
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from spatial_egt.common import get_data_path, theme_colors


def read_coords(row, raw_data_path):
    """Get the cell counts at each time step

    :param row: A row of the payoff dataframe
    :type row: Pandas Series
    :param raw_data_path: Path to the coordinate data
    :type raw_data_path: str
    :return: dataframe with cell counts
    :rtype: Pandas Dataframe
    """
    # Read coordinate file for the sample represented in the row
    source = row["source"]
    sample = row["sample"]
    df = pd.DataFrame()
    for seed in os.listdir(f"{raw_data_path}/{source}/{sample}"):
        path = f"{raw_data_path}/{source}/{sample}/{seed}/2Dcoords.csv"
        if not os.path.isfile(path):
            continue
        coords = pd.read_csv(path)
        coords["seed"] = seed
        df = pd.concat([df, coords])
    # Get the count of each cell type at each time step
    df = df[["seed", "model", "time", "type", "x"]]
    counts_r = df[df["type"] == 1].groupby(["model", "time", "type"]).count().reset_index()
    counts_s = df[df["type"] == 0].groupby(["model", "time", "type"]).count().reset_index()
    row["Sensitive"] = list(counts_s["x"].values)
    row["Resistant"] = list(counts_r["x"].values)
    row["Time"] = list(counts_s["time"].values)
    return row


def read_abm_data(data_type, source=None, sample_id=None):
    raw_data_path = get_data_path(data_type, "raw")
    data_path = get_data_path(data_type, ".")
    df = pd.read_csv(f"{data_path}/labels.csv")
    df["sample_id"] = df["sample"].str.split("-").str[0]
    if source is not None:
        df = df[(df["source"] == source)]
    if sample_id is not None:
        df = df[(df["sample_id"] == sample_id)]
    df["radii"] = df["sample"].str.split("-").str[1]

    abm_counts = df.apply(read_coords, axis=1, args=(raw_data_path,))
    abm_counts["sample"] = abm_counts["sample_id"]
    abm_counts = abm_counts[["source", "sample", "radii", "Time", "Sensitive", "Resistant"]]
    df_abm = abm_counts.explode(["Time", "Sensitive", "Resistant"])
    df_abm = pd.melt(
        df_abm,
        id_vars=["source", "sample", "radii", "Time"],
        value_vars=["Sensitive", "Resistant"],
        var_name="CellType",
        value_name="Count",
    )
    df_abm["TimePoint"] = df_abm.groupby(["source", "sample", "radii"]).cumcount()
    df_abm["data_type"] = "in_silico"
    return df_abm


def map_cell_type(df):
    df["CellType"] = df["CellType"].str.lower()
    df["type"] = "Sensitive"
    df.loc[df["CellType"].str.contains("mcherry"), "type"] = "Resistant"
    df["CellType"] = df["type"]
    df = df.drop("type", axis=1)
    return df


def read_exp_data(source=None, sample_id=None):
    data_path = get_data_path("in_vitro_pc9", ".")
    df = pd.read_csv(f"{data_path}/labels.csv")
    if source is not None:
        df = df[(df["source"] == source)]
    df_exp = pd.DataFrame()
    for source in df["source"].unique():
        counts_name = f"{source}_counts_df_processed.csv"
        raw_data_path = get_data_path("in_vitro_pc9", "raw")
        df_i = pd.read_csv(f"{raw_data_path}/{source}/{counts_name}")
        df_i = map_cell_type(df_i)
        df_i["source"] = source
        df_i["sample"] = df_i["PlateId"].astype(str) + "_" + df_i["WellId"]
        df_exp = pd.concat([df_exp, df_i[["source", "sample", "Time", "CellType", "Count"]]])
    if sample_id is not None:
        df_exp = df_exp[df_exp["sample"] == sample_id]
    df_exp["TimePoint"] = df_exp.groupby(["source", "sample"]).cumcount()
    df_exp["data_type"] = "in_vitro"
    df_exp["radii"] = "unk_unk_unk"
    return df_exp


def visualize(data_type, source, sample_id):
    df_abm = read_abm_data(data_type, source, sample_id)
    df_exp = read_exp_data(source, sample_id)
    df = pd.concat([df_exp, df_abm])
    df = df[df["Time"] <= 72]

    save_loc = get_data_path(data_type, "images")
    hue_order = sorted(df["radii"].unique())
    palette = sns.color_palette("hls", len(hue_order) - 1) + ["black"]
    g = sns.relplot(
        data=df,
        x="Time",
        y="Count",
        col="CellType",
        hue="radii",
        hue_order=hue_order,
        palette=palette,
        style="data_type",
        kind="line",
    )
    g.tight_layout()
    g.figure.patch.set_alpha(0.0)
    plt.savefig(f"{save_loc}/tune_radii {source} {sample_id}.png")


def plot_agg_radii(save_loc, df, name, hue=None):
    if hue is None:
        color = theme_colors[0]
        palette = None
        num_bars = np.max([len(df[name].unique()), 4])
    else:
        color = None
        palette = "Purples"
        num_bars = len(df[name].unique()) * len(df[hue].unique())
    fig, ax = plt.subplots(figsize=(num_bars // 2, 4))
    sns.barplot(
        data=df,
        x=name,
        y="MSE",
        hue=hue,
        palette=palette,
        color=color,
        order=sorted(df[name].unique()),
        ax=ax,
    )
    fig.tight_layout()
    fig.patch.set_alpha(0.0)
    fig.savefig(f"{save_loc}/tune_radii_{name}_{hue}.png", bbox_inches="tight")


def fit(data_type):
    df_abm = read_abm_data(data_type)
    df_exp = read_exp_data()

    df_abm = df_abm[df_abm["Time"] <= 72]
    df_exp = df_exp[df_exp["Time"] <= 72]

    abm_times = df_abm["Time"].unique()
    results = []
    for source in df_exp["source"].unique():
        df_source = df_exp[df_exp["source"] == source]
        for sample in df_source["sample"].unique():
            df_abm_i = df_abm[(df_abm["source"] == source) & (df_abm["sample"] == sample)]
            if len(df_abm_i) == 0:
                continue
            df_exp_i = df_source[df_source["sample"] == sample]
            df_exp_i = df_exp_i[df_exp_i["Time"].isin(abm_times)]
            df_abm_i = df_abm_i[df_abm_i["Time"].isin(df_exp_i["Time"].unique())]
            exp_s = df_exp_i[df_exp_i["CellType"] == "Sensitive"]["Count"].values
            exp_r = df_exp_i[df_exp_i["CellType"] == "Resistant"]["Count"].values
            for radii in df_abm_i["radii"].unique():
                df_abm_ir = df_abm_i[df_abm_i["radii"] == radii]
                abm_s = df_abm_ir[df_abm_ir["CellType"] == "Sensitive"]["Count"].values
                abm_r = df_abm_ir[df_abm_ir["CellType"] == "Resistant"]["Count"].values
                mse_s = np.square(np.subtract(exp_s, abm_s)).mean()
                mse_r = np.square(np.subtract(exp_r, abm_r)).mean()
                results.append(
                    {
                        "source": source,
                        "sample": sample,
                        "radii": radii,
                        "MSE": mse_r,
                        "CellType": "Resistant",
                    }
                )
                results.append(
                    {
                        "source": source,
                        "sample": sample,
                        "radii": radii,
                        "MSE": mse_s,
                        "CellType": "Sensitive",
                    }
                )
    df = pd.DataFrame(results)
    df["radii"] = df["radii"].str.replace("_", "\n")
    save_loc = get_data_path(data_type, "images")

    df["interaction_radius"] = df["radii"].str.split("\n").str[0].astype(int)
    df["repro_radius"] = df["radii"].str.split("\n").str[1].astype(int)
    plot_agg_radii(save_loc, df, "radii")
    plot_agg_radii(save_loc, df, "interaction_radius", "source")
    plot_agg_radii(save_loc, df, "repro_radius", "source")
    plot_agg_radii(save_loc, df, "interaction_radius")
    plot_agg_radii(save_loc, df, "repro_radius")

    df = df[["interaction_radius", "repro_radius", "MSE"]]
    df = df.groupby(["interaction_radius", "repro_radius"]).mean().reset_index()
    print(df.nsmallest(10, "MSE"))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        fit(*sys.argv[1:])
    elif len(sys.argv) == 4:
        visualize(*sys.argv[1:])
    else:
        print("Please see the module docstring for usage instructions.")
