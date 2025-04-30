import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from spatial_egt.common import game_colors, get_data_path

cell_colors = [game_colors["Sensitive Wins"], game_colors["Resistant Wins"]]


def plot_growth_over_time(df, save_loc):
    for plate_id in df["PlateId"].unique():
        df_plate = df[df["PlateId"] == plate_id]
        well_letters = sorted(df_plate["WellId"].str[0].unique())
        well_nums = sorted(df_plate["WellId"].str[1:].astype(int).unique())
        num_letters = len(well_letters)
        num_nums = len(well_nums)
        fig, ax = plt.subplots(num_letters, num_nums, 
                            figsize=(3*num_nums, 3*num_letters),
                            sharex=True, sharey=True)
        for l in range(len(well_letters)):
            for n in range(len(well_nums)):
                well = well_letters[l]+str(well_nums[n])
                sns.lineplot(data=df_plate[df_plate["WellId"] == well],
                             x="Time", y="Count", hue="CellType",
                             legend=False, ax=ax[l][n],
                             palette=cell_colors, linewidth=5,
                             hue_order=["sensitive", "resistant"])
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
        fig, ax = plt.subplots(num_letters, num_nums, 
                            figsize=(3*num_nums, 3*num_letters),
                            sharex=True, sharey=True)
        for l in range(len(well_letters)):
            for n in range(len(well_nums)):
                well = well_letters[l]+str(well_nums[n])
                sns.barplot(data=df_plate[df_plate["WellId"] == well],
                             y="DrugConcentration", x="Time", ax=ax[l][n])
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
        fig, ax = plt.subplots(num_letters, num_nums, 
                            figsize=(3*num_nums, 3*num_letters),
                            sharex=True, sharey=True)
        for l in range(len(well_letters)):
            for n in range(len(well_nums)):
                well = well_letters[l]+str(well_nums[n])
                sns.barplot(data=df_plate[df_plate["WellId"] == well],
                             y="SeededProportion_Parental", x="Time", ax=ax[l][n])
                ax[l][n].set(title=well, ylim=(0, 1))
        fig.patch.set_alpha(0.0)
        fig.tight_layout()
        plt.savefig(f"{save_loc}/plate{plate_id}_fs.png")
        plt.close()


def plot_game_gr(df, save_loc):
    sns.lmplot(data=df, x="Fraction_Sensitive", y="GrowthRate", 
                hue="CellType", col="DrugConcentration", legend=False,
                palette=cell_colors, hue_order=["sensitive", "resistant"],
                facet_kws=dict(sharey=False))
    plt.savefig(f"{save_loc}/gr_by_fs.png", transparent=True)
    plt.close()


def plot_game_gr_dc0(df, save_loc, source):
    df = df.loc[df["DrugConcentration"] == 0]
    facet = sns.lmplot(data=df, x="Fraction_Sensitive", y="GrowthRate", 
                       hue="CellType", legend=False, palette=cell_colors,
                       hue_order=["sensitive", "resistant"])
    facet.set_titles(template=source)
    plt.savefig(f"{save_loc}/gr_by_fs_dc0.png", transparent=True)
    plt.close()


def map_cell_type(df):
    df["CellType"] = df["CellType"].str.lower()
    df["type"] = "sensitive"
    df.loc[df["CellType"].str.contains("mcherry"), "type"] = "resistant"
    df["CellType"] = df["type"]
    return df


def main():
    raw_data_path = get_data_path("in_vitro/maxi", "raw")
    for exp_name in os.listdir(raw_data_path):
        exp_path = f"{raw_data_path}/{exp_name}"
        if os.path.isfile(exp_path):
            continue
        image_data_path = get_data_path("in_vitro", f"images/{exp_name}")

        growth_name = f"{exp_name}_growth_rate_df.csv"
        df = pd.read_csv(f"{raw_data_path}/{exp_name}/{growth_name}")
        df = map_cell_type(df)
        plot_game_gr(df, image_data_path)
        plot_game_gr_dc0(df, image_data_path, exp_name)

        counts_name = f"{exp_name}_counts_df_processed.csv"
        df = pd.read_csv(f"{raw_data_path}/{exp_name}/{counts_name}")
        df = map_cell_type(df)
        plot_growth_over_time(df, image_data_path)
        plot_drug_concentration(df, image_data_path)
        plot_fs(df, image_data_path)


if __name__ == "__main__":
    main()
