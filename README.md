# Code from the paper "i dont have a permanent title yet"

## Overview
Coming soon

## Installation
Clone repo: `git clone --recursive https://github.com/sydleither/agent-based-games`

Clone submodules: `git submodule update --init --recursive`

Create environment: `conda create --name spatial_egt --file spatial_egt/requirements.txt`
- Requires the [MuSpAn](https://www.muspan.co.uk/) package, which must be requested from the website.

Build ABM: see installation instructions in [EGT_HAL](https://github.com/sydleither/EGT_HAL) README

## Replicate Results

If you do not have access to an HPCC with SLURM, replace all instances of "sbatch job_*.sb" with "python3 -m".

### Process experimental data
Please email the corresponding author of the associated paper for access to the experimental data.
```
python3 -m data_processing.in_vitro.pc9.raw_to_processed_payoff
python3 -m data_processing.in_vitro.pc9.raw_to_processed_spatial
python3 spatial_egt/create_sbatch_job.py {email} processing 0-03:59 4gb spatial_egt {path}/agent-based-games {node}
python3 -m spatial_egt.data_processing.write_statistics_bash -dir in_vitro_pc9 -run_cmd "sbatch job_processing.sb"
bash run_in_vitro_pc9_72.sh
python3 -m spatial_egt.data_processing.statistics_to_features -dir in_vitro_pc9 -time 72 -label game
python3 -m data_analysis.in_vitro_payoffs
python3 -m spatial_egt.data_analysis.plot_gamespace -hue cell_types
python3 -m spatial_egt.classification.feature_exploration in_vitro_pc9 72 game CPCF_RS_Min CPCF_SR_Min
```

### Fit ABM parameters to experimental data
```
python3 -m data_generation.fit_data -run_cmd "sbatch job_abm.sb"
bash data/in_silico_fit/raw/run0.sh
bash data/in_silico_fit/raw/run1.sh
bash data/in_silico_fit/raw/run2.sh
bash data/in_silico_fit/raw/run3.sh
python3 spatial_egt/create_sbatch_job.py {email} processing 0-01:00 1gb spatial_egt {path}/agent-based-games {node}
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_payoff in_silico_fit
sbatch job_processing.sb data_analysis.fit_statistic
```

### Generate and process ABM data
Using SLURM (recommended):
```
python3 EGT_HAL/create_sbatch_job.py {email} abm 0-00:05 1gb {path}/agent-based-games/EGT_HAL {node}
python3 -m data_generation.main_data -lgr 0.02 -ugr 0.04 -x 300 -y 400 -m 50 -n 20 -freq 12 -end 120
bash data/in_silico/raw/HAL/run0.sh
bash data/in_silico/raw/HAL/run1.sh
bash data/in_silico/raw/HAL/run2.sh
python3 spatial_egt/create_sbatch_job.py {email} processing 0-01:00 1gb spatial_egt {path}/agent-based-games {node}
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_payoff in_silico
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_spatial in_silico 200
python3 spatial_egt/create_sbatch_job.py {email} statistics 1-00:00 4gb spatial_egt {path}/agent-based-games {node}
python3 -m spatial_egt.data_processing.write_statistics_bash in_silico 200 "sbatch job_statistics.sb"
bash run_in_silico_200.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_silico game 200
```

Running locally:
```
python3 -m data_generation.main_data data/in_silico/raw HAL 2500 42 "java -cp build/:lib/* SpatialEGT.SpatialEGT"
bash data/in_silico/raw/HAL/run0.sh
bash data/in_silico/raw/HAL/run1.sh
bash data/in_silico/raw/HAL/run2.sh
python3 -m data_processing.in_silico.raw_to_processed_payoff in_silico
python3 -m data_processing.in_silico.raw_to_processed_spatial in_silico 200
python3 -m spatial_egt.data_processing.write_statistics_bash in_silico "python3 -m"
bash run_in_silico_200.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_silico game 200
```

