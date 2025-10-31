"""
Writes config files and run scripts to sample the ABM
matching experiment data conditions to test the best
fitting interaction and reproduction radii
"""

import argparse
import os
import random

import numpy as np
import pandas as pd

from EGT_HAL.config_utils import write_config, write_run_scripts
from spatial_egt.common import get_data_path


def get_grid_size(data_dir):
    """Get maximum x and y of each spatial sample to find the grid size"""
    max_x = 0
    max_y = 0
    processed_data_path = get_data_path(data_dir, "processed", 72)
    for file_name in os.listdir(processed_data_path):
        df_sample = pd.read_csv(f"{processed_data_path}/{file_name}")
        max_x = np.max([max_x, df_sample["x"].max()])
        max_y = np.max([max_y, df_sample["y"].max()])
    return int(max_x - 1), int(max_y - 1)


def write_matching_configs(row, data_dir, run_command, space, end_time, grid_x, grid_y, seed):
    """ABM configs that match experimental data conditions"""
    random.seed(seed)
    if row["initial_fs"] > 0.95 or row["initial_fs"] < 0.05:
        return []
    run_output = []
    experiment_name = row["source"]
    run_str = f"{run_command} ../{data_dir} {experiment_name}"
    payoff = [row["a"], row["b"], row["c"], row["d"]]
    for grid_expansion in range(1, 4):
        for inter_radius in range(4, 12, 2):
            for repro_radius in range(4, inter_radius + 2, 2):
                config_name = f"{row['sample']}-{grid_expansion}_{inter_radius}_{repro_radius}"
                rep_seed = random.randint(0, 10000)
                abm_grid_x = grid_x // grid_expansion
                abm_grid_y = grid_y // grid_expansion
                avg_grid_length = (abm_grid_x + abm_grid_y) // 2
                write_config(
                    data_dir,
                    experiment_name,
                    config_name,
                    rep_seed,
                    payoff,
                    round(row["initial_density"] * abm_grid_x * abm_grid_y),
                    1 - row["initial_fs"],
                    x=abm_grid_x,
                    y=abm_grid_y,
                    interaction_radius=round(avg_grid_length * (inter_radius / 100)),
                    reproduction_radius=round(avg_grid_length * (repro_radius / 100)),
                    turnover=0.0,
                    write_freq=end_time,
                    ticks=end_time,
                )
                run_output.append(f"{run_str} {config_name} {space} {rep_seed}\n")
    return run_output


def main():
    """Generate scripts to run the ABM"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-abm_dir", "--abm_data_type", type=str, default="in_silico_fit")
    parser.add_argument("-exp_dir", "--exp_data_type", type=str, default="in_vitro_pc9")
    parser.add_argument("-run_cmd", "--run_command", type=str, default="sbatch job_abm.sb")
    parser.add_argument("-seed", "--seed", type=int, default=42)
    parser.add_argument("-end", "--end_time", type=int, default=72)
    args = parser.parse_args()

    abm_data_dir = get_data_path(args.abm_data_type, "raw")
    grid_x, grid_y = get_grid_size(args.exp_data_type)
    df = pd.read_csv(get_data_path(args.exp_data_type, ".") + "/labels.csv")
    run_output = df.apply(
        write_matching_configs,
        axis=1,
        args=(abm_data_dir, args.run_command, "2D", args.end_time, grid_x, grid_y, args.seed),
    )
    run_output = [x for y in run_output for x in y]
    write_run_scripts(abm_data_dir, ".", run_output)


if __name__ == "__main__":
    main()
