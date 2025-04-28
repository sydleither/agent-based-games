"""For each data source, process the spatial data

Expected usage:
python3 -m data_processing.in_vitro.raw_to_processed_spatial
"""

from data_processing.in_vitro.jinling.raw_to_processed_spatial import main as jinling_main
from data_processing.in_vitro.maxi.raw_to_processed_spatial import main as maxi_main


def main():
    """Process spatial data from both data sources"""
    #maxi_main()
    jinling_main()


if __name__ == "__main__":
    main()
