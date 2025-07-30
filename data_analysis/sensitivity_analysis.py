import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
import seaborn as sns
from sklearn.preprocessing import scale

from spatial_egt.classification.common import df_to_xy, get_feature_data
from spatial_egt.common import game_colors
from spatial_egt.classification.feature_plot_utils import format_df


def label_bars(ax, labels):
    bars = ax.patches
    if len(bars) != 0:
        sorted_bars = sorted(zip(bars, [b.get_y() for b in bars]), key=lambda x: x[1])
        sorted_bars = list(zip(*sorted_bars))[0]
        for b,bar in enumerate(sorted_bars):
            if len(labels[b]) > 100*bar.get_width():
                space_indices = [i for i, c in enumerate(labels[b]) if c == " "]
                middle_index = space_indices[len(space_indices) // 2]
                labels[b] = labels[b][:middle_index] + '\n' + labels[b][middle_index + 1:]
            ax.text(
                bar.get_width()/2, bar.get_y()+bar.get_height()/2,
                labels[b], ha="center", va="center",
                fontsize=10, color="black"
            )
    ax.set(yticklabels=[], ylabel="", xlabel="")
    ax.tick_params(left=False)


def plot_bars(save_loc, measurement, game, df):
    fig, ax = plt.subplots(3, 2, figsize=(6, 8))
    for j,data_type in enumerate(df["Model"].unique()):
        for i,time in enumerate(df["Time"].unique()):
            df_pair = df[(df["Model"] == data_type) & (df["Time"] == time)]
            df_pair = df_pair[df_pair[measurement] >= np.quantile(df_pair[measurement], 0.90)]
            df_pair = df_pair.sort_values(by=measurement, ascending=False)
            sns.barplot(data=df_pair, x=measurement, y="Feature", color=game_colors[game], ax=ax[i][j], legend=False)
            top_features = df_pair["Feature"].values
            label_bars(ax[i][j], top_features)
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
        for k,name in enumerate(feature_names):
            feature_i = i_features[k]
            feature_j = j_features[k]
            wass = wasserstein_distance(feature_i, feature_j)
            data.append({"Feature": name, "Game":game, "Earth Movers Distance": wass} | other)
    return data


def run_pairwise_distributions(data, int_to_class, feature_names):
    model_names = {"in_silico":"High Clustering", "in_silico2":"Medium Clustering", "in_silico3":"Low Clustering"}
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


def main():
    data = {}
    for data_type in ["in_silico", "in_silico2", "in_silico3"]:
        for time in [100, 200, 300]:
            _, df, feature_names_i = get_feature_data(
                data_type, time, "game", ["all"], "pairwise"
            )
            feature_names_i = sorted(feature_names_i)
            feature_df = df[feature_names_i+["game"]]
            X, y, int_to_class = df_to_xy(feature_df, feature_names_i, "game")
            X = scale(X, axis=0)
            data[(data_type, time)] = (X, y)

    save_loc = "data"
    df = run_pairwise_distributions(data, int_to_class, feature_names_i)
    df = format_df(df)
    for game in game_colors:
        if game == "Unknown":
            continue
        df_game = df[df["Game"] == game]
        plot_bars(save_loc, "Earth Movers Distance", game, df_game)


if __name__ == "__main__":
    main()
