"""Test the game quadrants of a payoff matrix under a drug gradient

Expected usage:
python3 -m data_generation.drug_gradient_payoff a b c d drug_concentration gradients

Where:
a, b, c, d: payoff matrix parameters
drug_concentration: max drug concentration that will be multipled by a and b
gradients: how many gradients the drug goes through before it is maxed out
"""

import sys

import matplotlib.pyplot as plt
import seaborn as sns


def main(a, b, c, d, drug_concentration, gradients):
    gradients = int(gradients)
    palette = sns.color_palette("flare", gradients)
    fig, ax = plt.subplots(figsize=(4, 3.5))
    for g in range(gradients):
        dc = drug_concentration * ((g+1)/gradients)
        print(dc, [a*(1-dc), b*(1-dc), c, d])
        ax.scatter(x=[c-a*(1-dc)], y=[b*(1-dc)-d], label=round(dc,2), s=50, color=palette[g])
    ax.axhline(0, color="black")
    ax.axvline(0, color="black")
    ax.set(xlabel="C-A", ylabel="B-D", title="Drug Gradient")
    fig.legend(title="Drug")
    fig.tight_layout()
    fig.patch.set_alpha(0)
    fig.savefig("data/drug_gradient_payoff.png", bbox_inches="tight", dpi=200)


if __name__ == "__main__":
    if len(sys.argv) == 7:
        main(*list(map(float, sys.argv[1:])))
    else:
        print("Please see the module docstring for usage instructions.")
