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

import sys

from EGT_HAL.config_utils import latin_hybercube_sample, write_config, write_run_scripts


def main(data_dir, experiment_name, num_samples, lhs_seed, run_command):
    """Generate scripts to run the ABM"""
    space = "2D"
    end_time = 100

    samples = latin_hybercube_sample(
        num_samples,
        ["A", "B", "C", "D", "fr"],
        [0.01, 0.01, 0.01, 0.01, 0.1],
        [0.04, 0.04, 0.04, 0.04, 0.9],
        [False, False, False, False, False],
        seed=lhs_seed,
    )

    run_output = []
    run_str = f"{run_command} ../{data_dir} {experiment_name}"
    for s, sample in enumerate(samples):
        config_name = str(s)
        seed = config_name
        payoff = [sample["A"], sample["B"], sample["C"], sample["D"]]
        write_config(
            data_dir,
            experiment_name,
            config_name,
            seed,
            payoff,
            2500,
            sample["fr"],
            x=500,
            y=500,
            interaction_radius=5,
            reproduction_radius=3,
            write_freq=20,
            ticks=end_time,
        )
        run_output.append(f"{run_str} {config_name} {space} {seed}\n")
    write_run_scripts(data_dir, experiment_name, run_output)


if __name__ == "__main__":
    if len(sys.argv) == 6:
        main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        print("Please see the module docstring for usage instructions.")
