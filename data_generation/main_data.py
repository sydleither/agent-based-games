"""Generate data used for main experiments.

Writes config files and run scripts to sample the ABM
across diverse payoff matrices and starting conditions.

Expected usage:
python3 -m data_generation.main_data experimental_data_dir, abm_data_dir, exp_name num_samples run_cmd

Where:
experimental_data_dir: the directory with the processed experimental data (e.g. "in_vitro_pc9")
abm_data_dir: the parent directory to save the ABM data to (e.g. "in_silico")
exp_name: the experiment name, which will be the subdirectory storing the data
num_samples: how many samples of the ABM to run
run_cmd: how to run the ABM samples
    e.g. "sbatch job_abm.sb" or "java -cp build/:lib/* SpatialEGT.SpatialEGT"
"""

import math
import sys

import numpy as np
import pandas as pd

from EGT_HAL.config_utils import latin_hybercube_sample, write_config, write_run_scripts
from data_generation.fit_experimental import get_grid_size
from spatial_egt.common import get_data_path


def main(experimental_data_dir, abm_data_dir, experiment_name, num_samples, run_command):
    """Generate scripts to run the ABM"""
    abm_data_dir = f"data/{abm_data_dir}/raw"
    space = "2D"
    end_time = 72
    grid_reduction = 16
    inter_radius = 6
    repro_radius = 4

    # calculate grid size based on experimental
    grid_x, grid_y = get_grid_size(experimental_data_dir)
    abm_grid_x = int(grid_x*(grid_reduction/100))
    abm_grid_y = int(grid_y*(grid_reduction/100))
    avg_grid_length = (abm_grid_x + abm_grid_y) // 2

    # get range of payoff values
    df_exp = pd.read_csv(get_data_path(experimental_data_dir, ".") + "/labels.csv")
    payoffs = df_exp[["a", "b", "c", "d"]].values
    payoffs = [x for y in payoffs for x in y]
    min_payoff = math.floor(min(payoffs) * 10**2) / 10**2
    max_payoff = math.ceil(max(payoffs) * 10**2) / 10**2

    # get range of initial densities and fraction sensitives
    min_density = np.max([0.01, df_exp["initial_density"].min()])
    max_density = df_exp["initial_density"].max()
    min_fs = np.max([0.05, df_exp["initial_fs"].min()])
    max_fs = np.min([0.95, df_exp["initial_fs"].max()])

    samples = latin_hybercube_sample(
        num_samples,
        ["A", "B", "C", "D", "initial_fs", "initial_density"],
        [min_payoff, min_payoff, min_payoff, min_payoff, min_fs, min_density],
        [max_payoff, max_payoff, max_payoff, max_payoff, max_fs, max_density],
        [False, False, False, False, False, False],
        seed=42,
    )

    run_output = []
    run_str = f"{run_command} ../{abm_data_dir} {experiment_name}"
    for s, sample in enumerate(samples):
        config_name = str(s)
        seed = config_name
        payoff = [sample["A"], sample["B"], sample["C"], sample["D"]]
        write_config(
            abm_data_dir,
            experiment_name,
            config_name,
            seed,
            payoff,
            int(sample["initial_density"] * abm_grid_x * abm_grid_y),
            1 - sample["initial_fs"],
            x=abm_grid_x,
            y=abm_grid_y,
            interaction_radius=int(avg_grid_length*(inter_radius/100)),
            reproduction_radius=int(avg_grid_length*(repro_radius/100)),
            write_freq=end_time,
            ticks=end_time,
        )
        run_output.append(f"{run_str} {config_name} {space} {seed}\n")
    write_run_scripts(abm_data_dir, experiment_name, run_output)


if __name__ == "__main__":
    if len(sys.argv) == 6:
        main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
    else:
        print("Please see the module docstring for usage instructions.")
