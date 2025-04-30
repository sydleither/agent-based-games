import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from spatial_egt.common import get_data_path


def plot_payoffs(save_loc, save_name, df):
    palette = sns.color_palette("hls", 4)
    hue_order = ["a", "b", "c", "d"]
    fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    sns.histplot(
        data=df,
        x="payoff",
        hue="letter",
        palette=palette,
        hue_order=hue_order,
        multiple="stack",
        ax=ax,
    )
    fig.patch.set_alpha(0.0)
    fig.tight_layout()
    plt.savefig(f"{save_loc}/payoffs{save_name}.png")


def get_samples(data_type, source):
    data_path = get_data_path(data_type, ".")
    df_labels = pd.read_csv(f"{data_path}/labels.csv")
    df_labels["sample"] = df_labels["sample"].astype(str)
    if source != "":
        df_labels = df_labels[df_labels["source"] == source]
    return df_labels


def main(data_type, source=""):
    save_name = ""
    if source != "":
        save_name += "_" + source

    image_data_path = get_data_path(data_type, "images")
    df = get_samples(data_type, source)
    df = pd.melt(
        df,
        id_vars=["source", "sample"],
        value_vars=["a", "b", "c", "d"],
        var_name="letter",
        value_name="payoff",
    )
    print(f"Lowest payoff value: {df['payoff'].min()}")
    print(f"Highest payoff value: {df['payoff'].max()}")

    plot_payoffs(image_data_path, save_name, df)


if __name__ == "__main__":
    if len(sys.argv) in (2, 3):
        main(*sys.argv[1:])
    else:
        print("Please provide the data type and (optionally) source")
