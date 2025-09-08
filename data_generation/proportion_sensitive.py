"""Generate data used for main experiments.

Writes config files and run scripts to sample the ABM
across diverse payoff matrices and starting conditions.

Expected usage:
python3 -m data_generation.main_data data_dir exp_name num_samples seed run_cmd

Where:
data_dir: the parent directory the data will be located in
exp_name: the experiment name, which will be the subdirectory storing the data
num_samples: how many samples of the ABM to run
seed: random seed for latin hypercube sampling
run_cmd: how to run the ABM samples
    e.g. "sbatch job_abm.sb" or "java -cp build/:lib/* SpatialEGT.SpatialEGT"
"""

import random
import sys

from EGT_HAL.config_utils import latin_hybercube_sample, write_config, write_run_scripts
from spatial_egt.common import calculate_game


def get_fr(payoff):
    game = calculate_game(*payoff)
    if game == "Unknown":
        return None
    if game == "Sensitive Wins":
        if random.random() < 0.5:
            return random.uniform(0.6, 0.9)
        else:
            return None
    elif game == "Resistant Wins":
        if random.random() < 0.5:
            return random.uniform(0.1, 0.4)
        else:
            return None
    else:
        if random.random() < 0.5:
            return random.uniform(0.6, 0.9)
        else:
            return random.uniform(0.1, 0.4)


def main(data_dir, experiment_name, num_samples, seed, run_command, interaction_radius=2, reproduction_radius=1, end_time=500):
    """Generate scripts to run the ABM"""
    space = "2D"

    samples = latin_hybercube_sample(
        2*num_samples,
        ["A", "B", "C", "D", "cells"],
        [0, 0, 0, 0, 50],
        [0.1, 0.1, 0.1, 0.1, 9500],
        [False, False, False, False, True],
        rnd=2,
        seed=seed,
    )

    run_output = []
    run_str = f"{run_command} ../{data_dir} {experiment_name}"
    for s, sample in enumerate(samples):
        config_name = str(s)
        seed = config_name
        payoff = [sample["A"], sample["B"], sample["C"], sample["D"]]
        fr = get_fr(payoff)
        if fr is None:
            continue
        write_config(
            data_dir,
            experiment_name,
            config_name,
            seed,
            payoff,
            sample["cells"],
            fr,
            x=100,
            y=100,
            interaction_radius=interaction_radius,
            reproduction_radius=reproduction_radius,
            turnover=0.009,
            write_freq=5,
            ticks=end_time
        )
        run_output.append(f"{run_str} {config_name} {space} {seed}\n")
    write_run_scripts(data_dir, experiment_name, run_output)


if __name__ == "__main__":
    if len(sys.argv) == 6:
        main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        print("Please see the module docstring for usage instructions.")
