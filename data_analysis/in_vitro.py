import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from data_processing.in_vitro.game_analysis_utils import calculate_growth_rates
from spatial_egt.common import game_colors, get_data_path

cell_colors = [game_colors["Sensitive Wins"], game_colors["Resistant Wins"]]


def plot_spatial(df, save_loc, exp_name):
    processed_data_path = get_data_path("in_vitro", "processed")
    for plate_id in df["plate"].unique():
        df_plate = df[df["plate"] == plate_id]
        well_letters = sorted(df_plate["well"].str[0].unique())
        well_nums = sorted(df_plate["well"].str[1:].astype(int).unique())
        num_letters = len(well_letters)
        num_nums = len(well_nums)
        if num_nums == 1:
            num_nums += 1
        fig, ax = plt.subplots(
            num_letters, num_nums, figsize=(3 * num_nums, 3 * num_letters), sharex=True, sharey=True
        )
        for l in range(len(well_letters)):
            for n in range(len(well_nums)):
                well = well_letters[l] + str(well_nums[n])
                sample_id = f"{plate_id}_{well}"
                file_name = f"{exp_name} {sample_id}.csv"
                try:
                    df_spatial = pd.read_csv(f"{processed_data_path}/{file_name}")
                except Exception:
                    continue
                df_spatial["color"] = df_spatial["type"].map(
                    {
                        "sensitive": game_colors["Sensitive Wins"],
                        "resistant": game_colors["Resistant Wins"],
                    }
                )
                ax[l][n].scatter(x=df_spatial["x"], y=df_spatial["y"], s=2, c=df_spatial["color"])
                ax[l][n].set(title=well)
        fig.patch.set_alpha(0.0)
        fig.tight_layout()
        plt.savefig(f"{save_loc}/plate{plate_id}_spatial.png")
        plt.close()


def plot_growth_over_time(df, save_loc):
    for plate_id in df["PlateId"].unique():
        df_plate = df[df["PlateId"] == plate_id]
        well_letters = sorted(df_plate["WellId"].str[0].unique())
        well_nums = sorted(df_plate["WellId"].str[1:].astype(int).unique())
        num_letters = len(well_letters)
        num_nums = len(well_nums)
        fig, ax = plt.subplots(
            num_letters, num_nums, figsize=(3 * num_nums, 3 * num_letters), sharex=True, sharey=True
        )
        for l in range(len(well_letters)):
            for n in range(len(well_nums)):
                well = well_letters[l] + str(well_nums[n])
                sns.lineplot(
                    data=df_plate[df_plate["WellId"] == well],
                    x="Time",
                    y="Count",
                    hue="CellType",
                    legend=False,
                    ax=ax[l][n],
                    palette=cell_colors,
                    linewidth=5,
                    hue_order=["sensitive", "resistant"],
                )
                ax[l][n].set(title=well)
        fig.patch.set_alpha(0.0)
        fig.tight_layout()
        plt.savefig(f"{save_loc}/plate{plate_id}_gr.png")
        plt.close()


def plot_drug_concentration(df, save_loc):
    df = df[df["Time"] == 0]
    for plate_id in df["PlateId"].unique():
        df_plate = df[df["PlateId"] == plate_id]
        max_drug = df_plate["DrugConcentration"].max()
        well_letters = sorted(df_plate["WellId"].str[0].unique())
        well_nums = sorted(df_plate["WellId"].str[1:].astype(int).unique())
        num_letters = len(well_letters)
        num_nums = len(well_nums)
        fig, ax = plt.subplots(
            num_letters, num_nums, figsize=(3 * num_nums, 3 * num_letters), sharex=True, sharey=True
        )
        for l in range(len(well_letters)):
            for n in range(len(well_nums)):
                well = well_letters[l] + str(well_nums[n])
                sns.barplot(
                    data=df_plate[df_plate["WellId"] == well],
                    y="DrugConcentration",
                    x="Time",
                    ax=ax[l][n],
                )
                ax[l][n].set(title=well, ylim=(0, max_drug))
        fig.patch.set_alpha(0.0)
        fig.tight_layout()
        plt.savefig(f"{save_loc}/plate{plate_id}_drugcon.png")
        plt.close()


def plot_fs(df, save_loc):
    df = df[df["Time"] == 0]
    for plate_id in df["PlateId"].unique():
        df_plate = df[df["PlateId"] == plate_id]
        well_letters = sorted(df_plate["WellId"].str[0].unique())
        well_nums = sorted(df_plate["WellId"].str[1:].astype(int).unique())
        num_letters = len(well_letters)
        num_nums = len(well_nums)
        fig, ax = plt.subplots(
            num_letters, num_nums, figsize=(3 * num_nums, 3 * num_letters), sharex=True, sharey=True
        )
        for l in range(len(well_letters)):
            for n in range(len(well_nums)):
                well = well_letters[l] + str(well_nums[n])
                sns.barplot(
                    data=df_plate[df_plate["WellId"] == well],
                    y="SeededProportion_Parental",
                    x="Time",
                    ax=ax[l][n],
                )
                ax[l][n].set(title=well, ylim=(0, 1))
        fig.patch.set_alpha(0.0)
        fig.tight_layout()
        plt.savefig(f"{save_loc}/plate{plate_id}_fs.png")
        plt.close()


def plot_game_gr(df, save_loc):
    sns.lmplot(
        data=df,
        x="Fraction_Sensitive",
        y="GrowthRate",
        hue="CellType",
        col="DrugConcentration",
        legend=False,
        palette=cell_colors,
        hue_order=["sensitive", "resistant"],
        facet_kws=dict(sharey=False),
    )
    plt.savefig(f"{save_loc}/gr_by_fs.png", transparent=True)
    plt.close()


def map_cell_type(df):
    df["CellType"] = df["CellType"].str.lower()
    df["type"] = "sensitive"
    df.loc[df["CellType"].str.contains("mcherry"), "type"] = "resistant"
    df["CellType"] = df["type"]
    return df


def main():
    data_path = get_data_path("in_vitro", ".")
    growth_rate_window = [24, 72]
    df_labels = pd.read_csv(f"{data_path}/labels.csv")
    for exp_name in df_labels["source"].unique():
        image_data_path = get_data_path("in_vitro", f"images/{exp_name}")
        if exp_name == "jinling":
            raw_data_path = get_data_path("in_vitro", "raw/jinling")
            counts_df = pd.read_csv(f"{raw_data_path}/count_data.csv")
            cell_types = ["Sensitive", "Resistant"]
            growth_rate_df = calculate_growth_rates(counts_df, growth_rate_window, cell_types)
            counts_df["type"] = counts_df["CellType"].str.lower()
            counts_df["CellType"] = counts_df["type"]
            growth_rate_df["type"] = growth_rate_df["CellType"].str.lower()
            growth_rate_df["CellType"] = growth_rate_df["type"]
        else:
            raw_data_path = get_data_path("in_vitro", "raw/maxi")
            exp_path = f"{raw_data_path}/{exp_name}"
            if os.path.isfile(exp_path):
                continue
            growth_name = f"{exp_name}_growth_rate_df.csv"
            growth_rate_df = pd.read_csv(f"{raw_data_path}/{exp_name}/{growth_name}")
            growth_rate_df = map_cell_type(growth_rate_df)
            counts_name = f"{exp_name}_counts_df_processed.csv"
            counts_df = pd.read_csv(f"{raw_data_path}/{exp_name}/{counts_name}")
            counts_df = map_cell_type(counts_df)
        plot_growth_over_time(counts_df, image_data_path)
        plot_drug_concentration(counts_df, image_data_path)
        plot_fs(counts_df, image_data_path)
        plot_game_gr(growth_rate_df, image_data_path)
        plot_spatial(df_labels[df_labels["source"] == exp_name], image_data_path, exp_name)


if __name__ == "__main__":
    main()
