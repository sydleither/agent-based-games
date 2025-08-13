import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from scipy.integrate import trapezoid
import seaborn as sns
import warnings

from spatial_egt.classification.common import get_feature_data
from spatial_egt.common import theme_colors


warnings.filterwarnings("ignore")


def plot_overlaps2(save_loc, df):
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    sns.violinplot(df, x="Spatial Scale Pair", y="Overlap", cut=0, color=theme_colors[0], ax=ax[0])
    sns.violinplot(df, x="Time", y="Overlap", cut=0, color=theme_colors[0], ax=ax[1])
    sns.violinplot(df, x="Game", y="Overlap", cut=0, color=theme_colors[0], ax=ax[2])
    for i in range(3):
        ax[i].set_xticklabels(ax[i].get_xticklabels(), rotation=45)
    fig.suptitle("Feature Distribution Overlap Across Parameters")
    fig.tight_layout()
    fig.patch.set_alpha(0)
    fig.savefig(f"{save_loc}/sa_all.png", dpi=200)


def plot_overlaps(save_loc, df, focal, subs):
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    sns.violinplot(df, x=focal, y="Overlap", cut=0, color=theme_colors[0], ax=ax[0])
    sns.violinplot(df, x=focal, y="Overlap", cut=0, hue=subs[0], palette="husl", ax=ax[1])
    sns.violinplot(df, x=focal, y="Overlap", cut=0, hue=subs[1], palette="husl", ax=ax[2])
    if focal == "Game":
        for i in range(3):
            ax[i].set_xticklabels(ax[i].get_xticklabels(), rotation=45)
    fig.suptitle(f"{focal} Feature Distribution Overlap")
    fig.tight_layout()
    fig.patch.set_alpha(0)
    fig.savefig(f"{save_loc}/sa_{focal}.png", dpi=200)


def get_xdata(dist1, dist2):
    minimum = np.min([dist1.min(), dist2.min()])
    maximum = np.max([dist1.max(), dist2.max()])
    return np.linspace(minimum, maximum, 50)


def overlap(df, feature_names):
    models = df["Model"].unique()
    data = []
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            model1 = models[i]
            model2 = models[j]
            for time in df["Time"].unique():
                for game in df["game"].unique():
                    df1 = df[(df["Model"] == model1) & (df["Time"] == time) & (df["game"] == game)]
                    df2 = df[(df["Model"] == model2) & (df["Time"] == time) & (df["game"] == game)]
                    for feature in feature_names:
                        xdata = get_xdata(df1[feature], df2[feature])
                        kde1 = gaussian_kde(df1[feature])
                        kde2 = gaussian_kde(df2[feature])
                        pdf1 = kde1(xdata)
                        pdf2 = kde2(xdata)
                        overlap = np.min([pdf1, pdf2], axis=0)
                        area = trapezoid(overlap, xdata)
                        data.append(
                            {
                                "Model1": model1,
                                "Model2": model2,
                                "Time": time,
                                "Game": game,
                                "Feature": feature,
                                "Overlap": area,
                            }
                        )

    df_p = pd.DataFrame(data)
    df_p["Spatial Scale Pair"] = df_p["Model1"] + "\n" + df_p["Model2"]

    feature_overlaps = df_p[["Feature", "Overlap"]].groupby(["Feature"]).mean()
    print(feature_overlaps.reset_index().sort_values(by=["Overlap"]))
    print(df_p[["Game", "Overlap"]].groupby(["Game"]).mean())
    print(df_p[["Time", "Overlap"]].groupby(["Time"]).mean())
    print(df_p[["Model1", "Model2", "Overlap"]].groupby(["Model1", "Model2"]).mean())
    return df_p


def main():
    df = pd.DataFrame()
    for data_type in ["in_silico", "in_silico2", "in_silico3"]:
        for time in [100, 200, 300]:
            _, feature_df, feature_names_i = get_feature_data(data_type, time, "game", ["all"])
            feature_names_i = sorted(feature_names_i)
            feature_df = feature_df[feature_names_i + ["game"]]
            feature_df["Model"] = data_type
            feature_df["Time"] = time
            df = pd.concat([df, feature_df])
    df["Model"] = df["Model"].map(
        {"in_silico": "High", "in_silico2": "Medium", "in_silico3": "Low"}
    )

    save_loc = "data"
    df_p = overlap(df, feature_names_i)
    df_p["Time"] = df_p["Time"].astype(str)
    plot_overlaps(save_loc, df_p, "Game", ["Time", "Spatial Scale Pair"])
    plot_overlaps(save_loc, df_p, "Time", ["Game", "Spatial Scale Pair"])
    plot_overlaps(save_loc, df_p, "Spatial Scale Pair", ["Time", "Game"])
    plot_overlaps2(save_loc, df_p)


if __name__ == "__main__":
    main()
