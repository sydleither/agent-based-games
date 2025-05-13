"""Generate data used for main experiments.

Writes config files and run scripts to sample the ABM matching experiment data conditions
to test the best fitting interaction and reproduction radii.

Expected usage:
python3 -m data_generation.fit_experimental abm_data_dir experimental_data_dir run_cmd

Where:
abm_data_dir: the parent directory to save the ABM data to (e.g. "fit")
experimental_data_dir: the directory with the processed experimental data (e.g. "in_vitro_pc9")
run_cmd: how to run the ABM samples
    e.g. "sbatch job_abm.sb" or "java -cp build/:lib/* SpatialEGT.SpatialEGT"
"""

import os
import random
import sys

import numpy as np
import pandas as pd

from EGT_HAL.config_utils import write_config, write_run_scripts
from spatial_egt.common import get_data_path


random.seed(42)


def get_grid_size(data_dir):
    """Get maximum x and y of each spatial sample to find the grid size"""
    max_x = 0
    max_y = 0
    processed_data_path = get_data_path(data_dir, "processed")
    for file_name in os.listdir(processed_data_path):
        df_sample = pd.read_csv(f"{processed_data_path}/{file_name}")
        max_x = np.max([max_x, df_sample["x"].max()])
        max_y = np.max([max_y, df_sample["y"].max()])
    return int(max_x-1), int(max_y-1)


def write_matching_configs(row, data_dir, run_command, space, end_time, grid_x, grid_y):
    """ABM configs that match experimental data conditions"""
    if row["initial_fs"] in (0, 1):
        return []
    run_output = []
    experiment_name = row["source"]
    run_str = f"{run_command} ../{data_dir} {experiment_name}"
    payoff = [row["a"], row["b"], row["c"], row["d"]]
    for grid_reduction in range(10, 22, 2):
        for inter_radius in range(4, 12, 2):
            for repro_radius in range(4, inter_radius+2, 2):
                config_name = f"{row['sample']}-{grid_reduction}_{inter_radius}_{repro_radius}"
                seed = random.randint(0, 10000)
                abm_grid_x = int(grid_x*(grid_reduction/100))
                abm_grid_y = int(grid_y*(grid_reduction/100))
                avg_grid_length = (abm_grid_x + abm_grid_y) // 2
                write_config(
                    data_dir,
                    experiment_name,
                    config_name,
                    seed,
                    payoff,
                    int(row["initial_density"]),
                    1 - row["initial_fs"],
                    x=abm_grid_x,
                    y=abm_grid_y,
                    interaction_radius=int(avg_grid_length*(inter_radius/100)),
                    reproduction_radius=int(avg_grid_length*(repro_radius/100)),
                    turnover=0.0,
                    write_freq=end_time // 10,
                    ticks=end_time,
                )
                run_output.append(f"{run_str} {config_name} {space} {seed}\n")
    return run_output


def main(abm_data_dir, experimental_data_dir, run_command):
    """Generate scripts to run the ABM"""
    abm_data_dir = f"data/{abm_data_dir}/raw"
    space = "2D"
    end_time = 120

    grid_x, grid_y = get_grid_size(experimental_data_dir)
    df = pd.read_csv(get_data_path(experimental_data_dir, ".") + "/labels.csv")
    run_output = df.apply(
        write_matching_configs,
        axis=1,
        args=(abm_data_dir, run_command, space, end_time, grid_x, grid_y),
    )
    run_output = [x for y in run_output for x in y]
    write_run_scripts(abm_data_dir, ".", run_output)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(*sys.argv[1:])
    else:
        print("Please see the module docstring for usage instructions.")
