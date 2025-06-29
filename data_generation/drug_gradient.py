"""Drug gradient experiment

Expected usage:
python3 -m data_generation.drug_gradient data_dir exp_name

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
    end_time = 100

    samples = {
        "test": [0.07, 0.09, 0.05, 0.06]
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
            5000,
            0.5,
            x=100,
            y=100,
            gradient=1,
            null=0,
            drug_reduction=0.5,
            write_freq=end_time,
            ticks=end_time,
        )
    write_run_scripts(data_dir, experiment_name, run_output)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Please see the module docstring for usage instructions.")
