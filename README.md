# Code from the paper "i dont have a permanent title yet"

## Overview
Coming soon

## Installation
Clone repo: `git clone --recursive git@github.com:sydleither/spatial-egt.git`

Clone submodules: `git submodule update --init --recursive`

Create environment: `conda create --name spatial_egt --file spatial_egt/requirements.txt`
- Requires the [MuSpAn](https://www.muspan.co.uk/) package, which must be requested from the website.

Build ABM: see installation instructions in [EGT_HAL](https://github.com/sydleither/EGT_HAL) README

## Replicate Results

### Generate ABM Data and calculate spatial statistics
Using SLURM (recommended):
```
python3 EGT_HAL/create_sbatch_job.py {email} abm 0-00:05 1gb {path}/agent-based-games/EGT_HAL {node}
python3 -m data_generation.main_data data/in_silico/raw HAL 2500 42 "sbatch job_abm.sb"
bash data/in_silico/raw/HAL/run0.sh
bash data/in_silico/raw/HAL/run1.sh
bash data/in_silico/raw/HAL/run2.sh
python3 spatial_egt/create_sbatch_job.py {email} processing 0-01:00 1gb spatial_egt {path} {node}
sbatch job_processing.sb data_processing.in_silico.payoff_raw_to_processed
sbatch job_processing.sb data_processing.in_silico.spatial_raw_to_processed
```

Running locally:
```
python3 -m data_generation.main_data data/in_silico/raw HAL 2500 42 "java -cp build/:lib/* SpatialEGT.SpatialEGT"
bash data/in_silico/raw/HAL/run0.sh
bash data/in_silico/raw/HAL/run1.sh
bash data/in_silico/raw/HAL/run2.sh
python3 -m data_processing.in_silico.payoff_raw_to_processed
python3 -m data_processing.in_silico.spatial_raw_to_processed
```

## Replicate Supplement

