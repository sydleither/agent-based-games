import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from scipy.integrate import trapezoid
from scipy.stats import zscore
import seaborn as sns

from spatial_egt.classification.common import get_feature_data
from spatial_egt.common import game_colors


def get_xdata(dist1, dist2):
    minimum = np.min([dist1.min(), dist2.min()])
    maximum = np.max([dist1.max(), dist2.max()])
    return np.linspace(minimum, maximum, 50)


def significance(df, feature_names):
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
    df_p = df_p.drop(["Feature"], axis=1)
    print(df_p[["Game", "Overlap"]].groupby(["Game"]).mean())
    print(df_p[["Time", "Overlap"]].groupby(["Time"]).mean())
    print(df_p[["Model1", "Model2", "Overlap"]].groupby(["Model1", "Model2"]).mean())


def main():
    df = pd.DataFrame()
    for data_type in ["in_silico", "in_silico2", "in_silico3"]:
        for time in [100, 200, 300]:
            _, feature_df, feature_names_i = get_feature_data(data_type, time, "game", ["all"])
            feature_names_i = sorted(feature_names_i)
            feature_df = feature_df[feature_names_i + ["game"]]
            for feature_name in feature_names_i:
                feature_df[feature_name] = zscore(feature_df[feature_name])
            feature_df["Model"] = data_type
            feature_df["Time"] = time
            df = pd.concat([df, feature_df])

    save_loc = "data"
    significance(df, feature_names_i)


if __name__ == "__main__":
    main()
