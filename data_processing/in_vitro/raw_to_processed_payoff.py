"""

Expected usage:
python3 -m data_processing.in_vitro.raw_to_processed_payoff
"""

import pandas as pd

from spatial_egt.common import get_data_path
from data_processing.in_vitro.jinling.raw_to_processed_payoff import main as jinling_main
from data_processing.in_vitro.maxi.raw_to_processed_payoff import main as maxi_main


def main():
    """Calculate payoff data from both data sources then combine and save them"""
    data_path = get_data_path("in_vitro", ".")
    time_to_keep = 72
    df1 = maxi_main(time_to_keep)
    df2 = jinling_main(time_to_keep)
    df = pd.concat([df1, df2])
    df.to_csv(f"{data_path}/labels.csv", index=False)


if __name__ == "__main__":
    main()
