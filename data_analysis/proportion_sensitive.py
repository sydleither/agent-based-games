import sys

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from spatial_egt.common import game_colors, get_data_path


def plot_fs(save_loc, save_name, df, hue):
    if hue == "Game":
        palette = game_colors.values()
        hue_order = game_colors.keys()
    else:
        palette = sns.color_palette("hls", len(df[hue].unique()))
        hue_order = sorted(df[hue].unique())
    fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    sns.scatterplot(
        data=df, x="initial_fs", y="Proportion_Sensitive", hue=hue, palette=palette, hue_order=hue_order, ax=ax
    )
    ax.plot(np.linspace(0, 1, 10), np.linspace(0, 1, 10), color="gray")
    fig.patch.set_alpha(0.0)
    fig.tight_layout()
    plt.savefig(f"{save_loc}/fs_{save_name}.png")


def get_samples(data_type, source, sample_ids):
    data_path = get_data_path(data_type, ".")
    df_labels = pd.read_csv(f"{data_path}/labels.csv")
    df_labels["sample"] = df_labels["sample"].astype(str)
    if source != "":
        df_labels = df_labels[df_labels["source"] == source]
    if sample_ids:
        df_labels = df_labels[df_labels["sample"].isin(sample_ids)]
    return df_labels


def main(data_type, hue, *filter_args):
    save_name = hue
    source = ""
    sample_ids = None
    if len(filter_args) == 1:
        source = filter_args[0]
        save_name += "_" + source
    if len(filter_args) > 1:
        source = filter_args[0]
        sample_ids = filter_args[1:]
        save_name += "_" + source + "_" + "_".join(sample_ids)

    image_data_path = get_data_path(data_type, "images")
    df = get_samples(data_type, source, sample_ids)
    features_data_path = get_data_path(data_type, "statistics")
    df_fs = pd.read_pickle(f"{features_data_path}/Proportion_Sensitive.pkl")
    df_fs["sample"] = df_fs["sample"].astype(str)
    df = df.merge(df_fs, on=["source", "sample"])

    hue_formatted = hue.replace("_", " ").title()
    df = df.rename({hue:hue_formatted}, axis=1)
    plot_fs(image_data_path, save_name, df, hue_formatted)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(*sys.argv[1:])
    else:
        print(
            "Please provide the data type, hue, (optionally) source, and (optionally) sample ids to plot."
        )
