import pandas as pd

from spatial_egt.classification.common import get_data_path, get_feature_data


def main():
    df = pd.DataFrame()
    for time in [100, 200, 300]:
        for data_type in ["in_silico", "in_silico2", "in_silico3"]:
            _, feature_df, feature_names_i = get_feature_data(data_type, time, "game", ["all"])
            feature_names_i = sorted(feature_names_i)
            feature_df = feature_df[feature_names_i + ["game"]]
            feature_df["source"] = data_type
            feature_df["sample"] = feature_df.index
            df = pd.concat([df, feature_df])
        path = get_data_path("in_silico_combo", "statistics", time)
        df.to_csv(f"{path}/features.csv", index=False)


if __name__ == "__main__":
    main()
