"""Visualize ABM across game quadrants

Expected usage:
python3 -m data_generation.sample_games data_dir exp_name

Where:
data_dir: the parent directory the data will be located in
exp_name: the experiment name, which will be the subdirectory storing the data
"""

import sys

from EGT_HAL.config_utils import write_config, write_run_scripts


def main(data_dir, experiment_name):
    """Generate scripts to run the ABM"""
    replicates = 1
    run_command = "java -cp build/:lib/* SpatialEGT.SpatialEGT"
    space = "2D"
    end_time = 200

    high = 0.06
    low = 0.01
    samples = {
        "Sensitive_Wins": [high, high, low, low],
        "Coexistence": [low, high, high, low],
        "Bistability": [high, low, low, high],
        "Resistant_Wins": [low, low, high, high],
    }

    run_output = []
    run_str = f"{run_command} ../{data_dir} {experiment_name}"
    for game, payoff in samples.items():
        config_name = game
        for r in range(replicates):
            seed = str(r)
            run_output.append(f"{run_str} {config_name} {space} {r} {end_time}\n")
            run_output.append(f"{run_str} {config_name} {space} {r}\n")
        write_config(
            data_dir,
            experiment_name,
            config_name,
            seed,
            payoff,
            10000,
            0.5,
            x=100,
            y=100,
            write_freq=end_time,
            ticks=end_time,
        )
    write_run_scripts(data_dir, experiment_name, run_output)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Please see the module docstring for usage instructions.")
