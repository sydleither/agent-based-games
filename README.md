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

### Generate ABM data and calculate spatial statistics
Using SLURM (recommended):
```
python3 EGT_HAL/create_sbatch_job.py {email} abm 0-00:05 1gb {path}/agent-based-games/EGT_HAL {node}
python3 -m data_generation.main_data data/in_silico/raw HAL 2500 42 "sbatch job_abm.sb"
bash data/in_silico/raw/HAL/run0.sh
bash data/in_silico/raw/HAL/run1.sh
bash data/in_silico/raw/HAL/run2.sh
python3 spatial_egt/create_sbatch_job.py {email} processing 0-01:00 1gb spatial_egt {path} {node}
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_payoff in_silico
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_spatial in_silico
python3 spatial_egt/create_sbatch_job.py {email} statistics 0-03:59 4gb spatial_egt {path} {node}
python3 -m spatial_egt.data_processing.write_statistics_bash in_silico "sbatch job_statistics.sb"
bash statistics_in_silico.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_silico game
```

Running locally:
```
python3 -m data_generation.main_data data/in_silico/raw HAL 2500 42 "java -cp build/:lib/* SpatialEGT.SpatialEGT"
bash data/in_silico/raw/HAL/run0.sh
bash data/in_silico/raw/HAL/run1.sh
bash data/in_silico/raw/HAL/run2.sh
python3 -m data_processing.in_silico.raw_to_processed_payoff in_silico
python3 -m data_processing.in_silico.raw_to_processed_spatial in_silico
python3 -m spatial_egt.data_processing.write_statistics_bash in_silico "python3 -m"
bash statistics_in_silico.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_silico game
```

### "Spatial patterns are qualitatively different across agent-based games"
```
python3 -m data_generation.sample_games data/in_silico_games/raw HAL
bash data/in_silico_games/raw/HAL/run0.sh
```

### "Pairs of games are distinguished by different spatial statistics"
'''
python3 -m spatial_egt.classification.feature_pairwise_games in_silico game noncorr
'''

### "Individually uninformative features can be synergistic"
```
python3 -m spatial_egt.classification.feature_entropy in_silico game noncorr
```

### "Machine learning can infer agent-based game from spatial features"
```
python3 -m spatial_egt.classification.feature_sequential in_silico game 0 noncor
```

### Experimental data section
#### Calculate spatial statistics
Using SLURM:
```
python3 spatial_egt/create_sbatch_job.py {email} processing 0-01:00 1gb spatial_egt {path} {node}
sbatch job_processing.sb data_processing.in_vitro.raw_to_processed_payoff
sbatch job_processing.sb data_processing.in_vitro.raw_to_processed_spatial
python3 spatial_egt/create_sbatch_job.py {email} statistics 0-03:59 4gb spatial_egt {path} {node}
python3 -m spatial_egt.data_processing.write_statistics_bash in_vitro "sbatch job_statistics.sb"
bash statistics_in_vitro.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_vitro game
```

Running locally:
```
python3 -m data_processing.in_vitro.raw_to_processed_payoff
python3 -m data_processing.in_vitro.raw_to_processed_spatial
python3 -m spatial_egt.data_processing.write_statistics_bash in_vitro "python3 -m"
bash statistics_in_vitro.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_vitro game
```

#### Generate game space
```
python3 -m spatial_egt.data_analysis.plot_gamespace in_vitro cell_types
```

## Replicate Supplement

### S2: Correlated feature clusters
```
python3 -m spatial_egt.classification.feature_exploration in_silico game all
```

### S3: Pairwise game distributions
```
python3 -m spatial_egt.classification.feature_pairwise_games in_silico game noncorr
```

### S4: Feature distributions
```
python3 -m spatial_egt.classification.feature_exploration in_silico game Proportion_Sensitive
python3 -m spatial_egt.classification.feature_exploration in_silico game NN_Resistant_Mean NN_Sensitive_Mean
python3 -m spatial_egt.classification.feature_exploration in_silico game ANNI_Resistant ANNI_Sensitive
python3 -m spatial_egt.classification.feature_exploration in_silico game NC_Resistant_SD NC_Sensitive_SD
python3 -m spatial_egt.classification.feature_exploration in_silico game CPCF_Resistant_Min
python3 -m spatial_egt.classification.feature_exploration in_silico game SES
```