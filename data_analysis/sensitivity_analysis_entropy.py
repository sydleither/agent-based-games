import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import zscore
import seaborn as sns

from spatial_egt.classification.common import get_feature_data
from spatial_egt.classification.DDIT.ddit import DDIT
from spatial_egt.common import game_colors


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
    top_features = [
        k for k, _ in sorted(entropies.items(), key=lambda item: item[1], reverse=True)
    ][0:3]
    label_entropy = ddit.entropy(label_name)
    ent = ddit.recursively_solve_formula(label_name + ":" + "&".join(top_features))
    ent = ent / label_entropy
    features = {f"Feature {i}": top_features[i] for i in range(len(top_features))}
    return features | {"Mutual Information": float(ent)}


def main():
    data = []
    for data_type in ["in_silico", "in_silico2", "in_silico3"]:
        for time in [100, 200, 300]:
            _, feature_df, feature_names_i = get_feature_data(data_type, time, "game", ["noncorr"])
            feature_df = feature_df[feature_names_i + ["game"]]
            for feature_name in feature_names_i:
                feature_df[feature_name] = zscore(feature_df[feature_name])
            top = get_entropy(feature_df, feature_names_i, "game")
            top = top | {"Model": data_type, "Time": time}
            data.append(top)

    save_loc = "data"
    df = pd.DataFrame(data)
    print(df)


if __name__ == "__main__":
    main()
