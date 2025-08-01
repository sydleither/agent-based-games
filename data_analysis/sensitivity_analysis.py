from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
import seaborn as sns
from sklearn.preprocessing import scale

from spatial_egt.classification.common import df_to_xy, get_feature_data
from spatial_egt.classification.feature_plot_utils import format_df
from spatial_egt.classification.DDIT.ddit import DDIT
from spatial_egt.common import game_colors


def label_bars(ax, labels):
    bars = ax.patches
    if len(bars) != 0:
        sorted_bars = sorted(zip(bars, [b.get_y() for b in bars]), key=lambda x: x[1])
        sorted_bars = list(zip(*sorted_bars))[0]
        for b, bar in enumerate(sorted_bars):
            if len(labels[b]) > 100 * bar.get_width():
                space_indices = [i for i, c in enumerate(labels[b]) if c == " "]
                middle_index = space_indices[len(space_indices) // 2]
                labels[b] = labels[b][:middle_index] + "\n" + labels[b][middle_index + 1 :]
            ax.text(
                bar.get_width() / 2,
                bar.get_y() + bar.get_height() / 2,
                labels[b],
                ha="center",
                va="center",
                fontsize=10,
                color="black",
            )


def plot_bars(save_loc, measurement, game, df):
    fig, ax = plt.subplots(3, 2, figsize=(6, 8))
    for j, data_type in enumerate(df["Model"].unique()):
        for i, time in enumerate(df["Time"].unique()):
            df_pair = df[(df["Model"] == data_type) & (df["Time"] == time)]
            df_pair = df_pair[df_pair[measurement] >= np.quantile(df_pair[measurement], 0.90)]
            df_pair = df_pair.sort_values(by=measurement, ascending=False)
            sns.barplot(
                data=df_pair,
                x=measurement,
                y="Feature",
                color=game_colors[game],
                ax=ax[i][j],
                legend=False,
            )
            top_features = df_pair["Feature"].values
            label_bars(ax[i][j], top_features)
            ax[i][j].set(yticklabels=[], ylabel="", xlabel="")
            ax[i][j].tick_params(left=False)
            if i == 0:
                ax[i][j].set_title(data_type, fontsize=12)
            if j == 0:
                ax[i][j].set_ylabel(time, fontsize=12)
            if i == 2:
                ax[i][j].set_xlabel(measurement, fontsize=12)
    fig.suptitle("Distance from High Clustering Model for each Feature", x=0.5, y=0.94)
    fig.subplots_adjust(wspace=0.15, hspace=0.2)
    fig.figure.patch.set_alpha(0.0)
    fig.savefig(f"{save_loc}/emd_{game}.png", bbox_inches="tight", dpi=200)
    plt.close()


def plot_violins(save_loc, measurement, df):
    fig, ax = plt.subplots(3, 2, figsize=(6, 8))
    colors = {k: v for k, v in game_colors.items() if k != "Unknown"}
    for j, data_type in enumerate(df["Model"].unique()):
        for i, time in enumerate(df["Time"].unique()):
            df_pair = df[(df["Model"] == data_type) & (df["Time"] == time)]
            sns.violinplot(
                data=df_pair,
                x=measurement,
                hue="Game",
                hue_order=colors.keys(),
                palette=colors.values(),
                inner="stick",
                cut=0,
                ax=ax[i][j],
                legend=False,
            )
            ax[i][j].set(yticklabels=[], ylabel="", xlabel="")
            ax[i][j].tick_params(left=False)
            if i == 0:
                ax[i][j].set_title(data_type, fontsize=12)
            if j == 0:
                ax[i][j].set_ylabel(time, fontsize=12)
            if i == 2:
                ax[i][j].set_xlabel(measurement, fontsize=12)
    fig.suptitle("Distance from High Clustering Model Across Games", x=0.5, y=0.94)
    fig.subplots_adjust(wspace=0.15, hspace=0.2)
    fig.figure.patch.set_alpha(0.0)
    fig.savefig(f"{save_loc}/emd.png", bbox_inches="tight", dpi=200)
    plt.close()


def pairwise_distributions(X_i, y_i, X_j, y_j, int_to_class, feature_names, other):
    data = []
    for g in range(len(int_to_class)):
        i_indices = [k for k in range(len(y_i)) if y_i[k] == g]
        i_features = [X_i[k] for k in i_indices]
        i_features = list(zip(*i_features))
        j_indices = [k for k in range(len(y_j)) if y_j[k] == g]
        j_features = [X_j[k] for k in j_indices]
        j_features = list(zip(*j_features))
        game = int_to_class[g]
        for k, name in enumerate(feature_names):
            feature_i = i_features[k]
            feature_j = j_features[k]
            wass = wasserstein_distance(feature_i, feature_j)
            data.append({"Feature": name, "Game": game, "Earth Movers Distance": wass} | other)
    return data


def run_pairwise_distributions(data, int_to_class, feature_names):
    model_names = {
        "in_silico": "High Clustering",
        "in_silico2": "Medium Clustering",
        "in_silico3": "Low Clustering",
    }
    rows = []
    for data_type in ["in_silico2", "in_silico3"]:
        for time in [100, 200, 300]:
            X_i = data[("in_silico", time)][0]
            y_i = data[("in_silico", time)][1]
            X_j = data[(data_type, time)][0]
            y_j = data[(data_type, time)][1]
            other = {"Time": time, "Model": model_names[data_type]}
            rows += pairwise_distributions(X_i, y_i, X_j, y_j, int_to_class, feature_names, other)
    return pd.DataFrame(rows)


def get_entropy(df, feature_names, label_name="game"):
    # initializations
    ddit = DDIT()

    # bin, register, and calculate mutual information of features
    nbins = int(np.ceil(np.log2(len(df)) + 1))
    entropies = {}
    ddit.register_column_tuple(label_name, tuple(df[label_name].values))
    for feature_name in feature_names:
        column_data = df[feature_name].values
        binned_column_data = pd.qcut(column_data, nbins, labels=False, duplicates="drop")
        ddit.register_column_tuple(feature_name, tuple(binned_column_data))
        entropies[feature_name] = ddit.recursively_solve_formula(f"{label_name}:{feature_name}")

    # calculate joint mutual information
    top_features = [k for k in sorted(entropies.items(), key=lambda item: item[1])][0:3]
    label_entropy = ddit.entropy(label_name)
    ent = ddit.recursively_solve_formula(label_name + ":" + "&".join(top_features))
    ent = ent / label_entropy
    features = {f"Feature {i}": top_features[i] for i in range(3)}
    return features | {"Mutual Information": float(ent)}


def entropy_plot(save_loc, df, feature_names):
    data = {}
    for model in df["Model"].unique():
        for time in df["Time"].unique():
            df_i = df[(df["Model"] == model) & (df["Time"] == time)]
            top = get_entropy(df_i, feature_names)
            top = top | {"Model":model, "Time":time}
            data = data | top
    df = pd.DataFrame(data)
    print(df)


def main():
    data = {}
    df_ent = pd.DataFrame()
    for data_type in ["in_silico", "in_silico2", "in_silico3"]:
        for time in [100, 200, 300]:
            _, feature_df, feature_names_i = get_feature_data(
                data_type, time, "game", ["all"], "pairwise"
            )
            feature_names_i = sorted(feature_names_i)
            feature_df = feature_df[feature_names_i + ["game"]]
            feature_df["Model"] = data_type
            feature_df["Time"] = time
            df_ent = pd.concat([df_ent, feature_df])
            X, y, int_to_class = df_to_xy(feature_df, feature_names_i, "game")
            X = scale(X, axis=0)
            data[(data_type, time)] = (X, y)

    save_loc = "data"
    # df_pw = run_pairwise_distributions(data, int_to_class, feature_names_i)
    # df_pw = format_df(df_pw)
    # for game in game_colors:
    #     if game == "Unknown":
    #         continue
    #     df_game = df_pw[df_pw["Game"] == game]
    #     plot_bars(save_loc, "Earth Movers Distance", game, df_game)
    # plot_violins(save_loc, "Earth Movers Distance", df_pw)
    entropy_plot(save_loc, df_ent, feature_names_i)


if __name__ == "__main__":
    main()
