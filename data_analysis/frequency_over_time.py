"""Plot ABM cell composition over time

Expected usage: python3 -m data_analysis.frequency_over_time data_type source

Where:
data_type: the name of the directory in data/ containing raw/ coordinates
source: the data source
"""

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from spatial_egt.common import game_colors, get_data_path


def main(data_type, source):
    raw_data_path = get_data_path(data_type, "raw")
    df = pd.DataFrame()
    for sample in os.listdir(f"{raw_data_path}/{source}"):
        if os.path.isfile(f"{raw_data_path}/{source}/{sample}"):
            continue
        for rep in os.listdir(f"{raw_data_path}/{source}/{sample}"):
            if os.path.isfile(f"{raw_data_path}/{source}/{sample}/{rep}"):
                continue
            coords = pd.read_csv(f"{raw_data_path}/{source}/{sample}/{rep}/2Dcoords.csv")
            coords = coords[["time", "type", "x"]]
            counts = coords.groupby(["time", "type"]).count().reset_index()
            counts["sample"] = sample
            df = pd.concat([counts, df])

    types = [0, 1]
    colors = [game_colors["Sensitive Wins"], game_colors["Resistant Wins"]]
    save_loc = get_data_path(data_type, "images")
    for sample in df["sample"].unique():
        df_sample = df[df["sample"] == sample]
        fig, ax = plt.subplots()
        sns.lineplot(
            data=df_sample, x="time", y="x", hue="type", ax=ax, hue_order=types, palette=colors, legend=False, lw=10
        )
        ax.axvline(x=200, color="gray", lw=10, ls="--")
        ax.set(xlabel=None, ylabel=None)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_linewidth(10)
        ax.spines["bottom"].set_linewidth(10)
        fig.patch.set_alpha(0.0)
        fig.tight_layout()
        plt.savefig(f"{save_loc}/{source}_{sample}_counts.png", bbox_inches="tight", dpi=200)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(*sys.argv[1:])
    else:
        print("Please see the module docstring for usage instructions.")
