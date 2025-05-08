"""Generate data used for main experiments.

Writes config files and run scripts to sample the ABM matching experiment data conditions
to test the best fitting interaction and reproduction radii.

Expected usage:
python3 -m data_generation.tune_radii data_dir run_cmd

Where:
data_dir: the parent directory the data will be located in
run_cmd: how to run the ABM samples
    e.g. "sbatch job_abm.sb" or "java -cp build/:lib/* SpatialEGT.SpatialEGT"
"""

import random
import sys

import pandas as pd

from EGT_HAL.config_utils import write_config, write_run_scripts
from spatial_egt.common import get_data_path


def write_matching_configs(row, data_dir, run_command, space, end_time):
    """ABM configs that match experimental data conditions"""
    if row["initial_fs"] in (0, 1):
        return []
    run_output = []
    experiment_name = row["source"]
    run_str = f"{run_command} ../{data_dir} {experiment_name}"
    payoff = [row["a"], row["b"], row["c"], row["d"]]
    for grid_size in range(100, 600, 100):
        for inter_radius in range(3, 18, 3):
            for repro_radius in range(3, inter_radius+3, 3):
                config_name = f"{row['sample']}-{grid_size}_{inter_radius}_{repro_radius}"
                seed = random.randint(0, 1000)
                write_config(
                    data_dir,
                    experiment_name,
                    config_name,
                    seed,
                    payoff,
                    int(row["initial_density"]),
                    1 - row["initial_fs"],
                    x=grid_size,
                    y=grid_size,
                    interaction_radius=inter_radius,
                    reproduction_radius=repro_radius,
                    turnover=0.0,
                    write_freq=end_time // 10,
                    ticks=end_time,
                )
                run_output.append(f"{run_str} {config_name} {space} {seed}\n")
    return run_output


def main(data_dir, run_command):
    """Generate scripts to run the ABM"""
    space = "2D"
    end_time = 120

    df = pd.read_csv(get_data_path("in_vitro", ".") + "/labels.csv")
    run_output = df.apply(
        write_matching_configs,
        axis=1,
        args=(data_dir, run_command, space, end_time),
    )
    run_output = [x for y in run_output for x in y]
    write_run_scripts(data_dir, ".", run_output)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(*sys.argv[1:])
    else:
        print("Please see the module docstring for usage instructions.")
