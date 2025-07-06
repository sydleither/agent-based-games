"""Drug gradient experiment

Expected usage:
python3 -m data_generation.drug_gradient data_dir exp_name

Where:
data_dir: the parent directory the data will be located in
exp_name: the experiment name, which will be the subdirectory storing the data
"""

import sys

import matplotlib.pyplot as plt
import seaborn as sns

from EGT_HAL.config_utils import write_config, write_run_scripts


def plot_gamespace_gradient(data_dir, samples):
    palette = sns.color_palette("flare", len(samples))
    fig, ax = plt.subplots(figsize=(4, 3.5))
    i = 0
    for name, payoff in samples.items():
        ax.scatter(x=[payoff[2]-payoff[0]], y=[payoff[1]-payoff[3]], label=name, s=50, color=palette[i])
        i += 1
    ax.axhline(0, color="black")
    ax.axvline(0, color="black")
    ax.set(xlabel="C-A", ylabel="B-D", title="Game Space Gradient")
    fig.legend(title="Drug")
    fig.tight_layout()
    fig.patch.set_alpha(0)
    fig.savefig(f"{data_dir}/gamespace_gradient.png", bbox_inches="tight", dpi=200)


def main(data_dir, experiment_name, run_command):
    """Generate scripts to run the ABM"""
    replicates = 10
    space = "2D"
    end_time = 200

    samples = {
        "0.0": [0.99, 1, 0.97, 0.75],
        "0.125": [0.67, 0.69, 0.75, 0.79],
        "0.25": [0.47, 0.42, 0.83, 0.70],
        "0.5": [0.37, -0.02, 0.86, 0.71],
        "1": [0.37, -0.4, 0.93, 0.72],
        #"2": [0.34, -0.5, 0.98, 0.74],
        #"4": [0.33, -0.6, 1.12, 0.79]
    }
    payoffs = [[round(x/10, 3) for x in payoff] for payoff in samples.values()]

    run_output = []
    run_str = f"{run_command} ../{data_dir} {experiment_name}"
    config_name = "gradient"
    for r in range(replicates):
        seed = str(r)
        run_output.append(f"{run_str} {config_name} {space} {r}\n")
        write_config(
            data_dir,
            experiment_name,
            config_name,
            seed,
            payoffs,
            125000,
            0.5,
            x=500,
            y=500,
            write_freq=end_time,
            ticks=end_time,
        )
    write_run_scripts(data_dir, experiment_name, run_output)
    plot_gamespace_gradient(data_dir, samples)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(*sys.argv[1:])
    else:
        print("Please see the module docstring for usage instructions.")
