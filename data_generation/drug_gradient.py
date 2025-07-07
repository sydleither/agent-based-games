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
    replicates = 20
    space = "2D"
    end_time = 200

    samples = {
        0.0: [0.042, 0.046486, 0.034767, 0.0312],
        0.001312: [0.037826, 0.038691, 0.034937, 0.0312],
        0.002625: [0.03461, 0.032585, 0.035105, 0.0312],
        0.00525: [0.029976, 0.023569, 0.035433, 0.0312],
        0.0105: [0.024485, 0.012302, 0.03606, 0.0312]
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
            interaction_radius=2,
            reproduction_radius=1,
            turnover=0.004,
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
