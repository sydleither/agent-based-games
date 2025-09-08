"""Generate data used for main experiments.

Writes config files and run scripts to sample the ABM
across diverse payoff matrices and starting conditions.
"""

import argparse

from EGT_HAL.config_utils import latin_hybercube_sample, write_config, write_run_scripts


def main():
    """Generate scripts to run the ABM"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_silico")
    parser.add_argument("-exp", "--experiment_name", type=str, default="HAL")
    parser.add_argument("-run_cmd", "--run_command", type=str, default="sbatch job_abm.sb")
    parser.add_argument("-seed", "--seed", type=int, default=42)
    parser.add_argument("-num", "--num_samples", type=int, default=1000)
    parser.add_argument("-lgr", "--lower_game_range", type=float, default=0.0)
    parser.add_argument("-ugr", "--upper_game_range", type=float, default=0.1)
    parser.add_argument("-x", "--grid_x", type=int, default=100)
    parser.add_argument("-y", "--grid_y", type=int, default=100)
    parser.add_argument("-m", "--interaction_radius", type=int, default=2)
    parser.add_argument("-n", "--reproduction_radius", type=int, default=1)
    parser.add_argument("-freq", "--write_freq", type=int, default=10)
    parser.add_argument("-end", "--end_time", type=int, default=100)
    args = parser.parse_args()

    lgr = args.lower_game_range
    ugr = args.upper_game_range
    capacity = args.grid_x * args.grid_y

    samples = latin_hybercube_sample(
        args.num_samples,
        ["A", "B", "C", "D", "fr", "cells"],
        [lgr, lgr, lgr, lgr, 0.2, 0.2*capacity],
        [ugr, ugr, ugr, ugr, 0.8, 0.8*capacity],
        [False, False, False, False, False, True],
        rnd=3,
        seed=args.seed,
    )

    run_output = []
    run_str = f"{args.run_command} ../data/{args.data_type}/raw {args.experiment_name}"
    for s, sample in enumerate(samples):
        config_name = str(s)
        seed = config_name
        payoff = [sample["A"], sample["B"], sample["C"], sample["D"]]
        write_config(
            args.data_type,
            args.experiment_name,
            config_name,
            seed,
            payoff,
            sample["cells"],
            sample["fr"],
            x=args.grid_x,
            y=args.grid_y,
            interaction_radius=args.interaction_radius,
            reproduction_radius=args.reproduction_radius,
            turnover=0.009,
            write_freq=args.write_freq,
            ticks=args.end_time,
        )
        run_output.append(f"{run_str} {config_name} 2D {seed}\n")
    write_run_scripts(args.data_type, args.experiment_name, run_output)


if __name__ == "__main__":
    main()
