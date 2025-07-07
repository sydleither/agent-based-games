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
    end_time = 500

    samples = {
        0.0: [0.030000, 0.033204, 0.024834, 0.022286],
        0.0009: [0.027019, 0.027636, 0.024955, 0.022286],
        0.0019: [0.024721, 0.023275, 0.025075, 0.022286],
        0.0037: [0.021411, 0.016835, 0.025309, 0.022286],
        0.0075: [0.017489, 0.008787, 0.025757, 0.022286]
    }
    payoffs = list(samples.values())

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
            write_freq=100,
            ticks=end_time,
        )
    write_run_scripts(data_dir, experiment_name, run_output)
    plot_gamespace_gradient(data_dir, samples)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(*sys.argv[1:])
    else:
        print("Please see the module docstring for usage instructions.")
