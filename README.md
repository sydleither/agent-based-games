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

### Generate ABM Data and calculate spatial statistics
Using SLURM (recommended):
```
python3 EGT_HAL/create_sbatch_job.py {email} abm 0-00:05 1gb {path}/agent-based-games/EGT_HAL {node}
python3 -m data_generation.main_data data/in_silico/raw HAL 2500 42 "sbatch job_abm.sb"
bash data/in_silico/raw/HAL/run0.sh
bash data/in_silico/raw/HAL/run1.sh
bash data/in_silico/raw/HAL/run2.sh
python3 spatial_egt/create_sbatch_job.py {email} processing 0-01:00 1gb spatial_egt {path}/agent-based-games {node}
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_payoff in_silico
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_spatial in_silico
python3 spatial_egt/create_sbatch_job.py {email} statistics 1-00:00 4gb spatial_egt {path}/agent-based-games {node}
python3 -m spatial_egt.data_processing.write_statistics_bash in_silico "sbatch job_statistics.sb"
bash run_in_silico.sh
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
bash run_in_silico.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_silico game
```

### "Spatial patterns are qualitatively different across agent-based games"
```
python3 -m data_generation.sample_games data/in_silico_games/raw HAL
cd EGT_HAL
bash ../data/in_silico_games/raw/HAL/run0.sh
python3 -m data_analysis.frequency_over_time in_silico_games HAL
python3 -m data_processing.in_silico.raw_to_processed_spatial in_silico_games
python3 -m spatial_egt.data_analysis.plot_spatial in_silico_games HAL Sensitive_Wins Coexistence Bistability Resistant_Wins
```

### "Pairs of games are distinguished by different spatial statistics"
```
python3 -m spatial_egt.classification.feature_pairwise_games in_silico game noncorr
```

### "Individually uninformative features can be synergistic"
```
python3 -m spatial_egt.classification.feature_entropy in_silico game noncorr
```

### "Machine learning can infer agent-based game from spatial features"
```
python3 -m spatial_egt.classification.model_eval in_silico game ANNI_RS ANNI_SR CPCF_SS_Min Entropy KL_Divergence NC_RS_SD NC_SR_SD Proportion_Sensitive Ripleys_k_RS_Max SES Spatial_Subsample_SD
```

### "IDK"
HPCC
```
python3 EGT_HAL/create_sbatch_job.py {email} abm 0-00:05 1gb {path}/agent-based-games/EGT_HAL {node}
python3 -m data_generation.drug_gradient data/in_silico_drug/raw HAL "sbatch job_abm.sb"
bash data/in_silico_drug/raw/HAL/run0.sh
sbatch job_processing.sb data_processing.in_silico.drug_gradient in_silico_drug 100
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_payoff in_silico_drug_split
sbatch job_processing.sb data_processing.in_silico.raw_to_processed_spatial in_silico_drug_split
python3 -m spatial_egt.data_processing.write_statistics_bash in_silico_drug_split "sbatch job_statistics.sb"
bash run_in_silico_drug_split.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_silico_drug_split game
python3 -m spatial_egt.classification.model_train in_silico game ANNI_RS ANNI_SR CPCF_RR_Max CPCF_RR_Min CPCF_RS_Min CPCF_SR_Max CPCF_SS_Min KL_Divergence Local_i_Resistant_Mean NC_RS_SD NC_SR_SD Proportion_Sensitive Ripleys_k_RS_Max
python3 -m data_analysis.drug_gradient_eval in_silico in_silico_drug_split game ANNI_RS ANNI_SR CPCF_RR_Max CPCF_RR_Min CPCF_RS_Min CPCF_SR_Max CPCF_SS_Min KL_Divergence Local_i_Resistant_Mean NC_RS_SD NC_SR_SD Proportion_Sensitive Ripleys_k_RS_Max
```

Local
```
python3 -m data_generation.drug_gradient data/in_silico_drug/raw HAL "java -cp build/:lib/* SpatialEGT.SpatialEGT"
cd EGT_HAL
bash ../data/in_silico_drug/raw/HAL/run0.sh
python3 -m data_processing.in_silico.drug_gradient in_silico_drug 100
python3 -m data_processing.in_silico.raw_to_processed_payoff in_silico_drug_split
python3 -m data_processing.in_silico.raw_to_processed_spatial in_silico_drug_split
python3 -m spatial_egt.data_processing.write_statistics_bash in_silico_drug_split "python3 -m"
bash run_in_silico_drug_split.sh
python3 -m spatial_egt.data_processing.statistics_to_features in_silico_drug_split game
python3 -m spatial_egt.classification.model_train in_silico game ANNI_RS ANNI_SR CPCF_RR_Max CPCF_RR_Min CPCF_RS_Min CPCF_SR_Max CPCF_SS_Min KL_Divergence Local_i_Resistant_Mean NC_RS_SD NC_SR_SD Proportion_Sensitive Ripleys_k_RS_Max
python3 -m data_analysis.drug_gradient_eval in_silico in_silico_drug_split game ANNI_RS ANNI_SR CPCF_RR_Max CPCF_RR_Min CPCF_RS_Min CPCF_SR_Max CPCF_SS_Min KL_Divergence Local_i_Resistant_Mean NC_RS_SD NC_SR_SD Proportion_Sensitive Ripleys_k_RS_Max
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
python3 -m spatial_egt.classification.feature_exploration in_silico game Proportion_Sensitive Entropy SES NC_SR_SD CPCF_RS_Min Local_i_Sensitive_Skew
python3 -m spatial_egt.classification.feature_exploration in_silico game noncorr
```

### S5: Mutual information
```
python3 -m spatial_egt.classification.feature_entropy in_silico game noncorr
```

### S6: Machine learning
```
python3 -m spatial_egt.classification.feature_sequential in_silico game {i} noncorr
python3 -m spatial_egt.classification.feature_sequential_analysis in_silico game noncorr
python3 -m spatial_egt.classification.model_tuning in_silico game ANNI_RS ANNI_SR CPCF_RR_Max CPCF_RR_Min CPCF_RS_Min CPCF_SR_Max CPCF_SS_Min KL_Divergence Local_i_Resistant_Mean NC_RS_SD NC_SR_SD Proportion_Sensitive Ripleys_k_RS_Max
```

## Suite of analyzes to overview data
```
python3 -m spatial_egt.classification.feature_exploration in_silico game all
python3 -m spatial_egt.classification.feature_exploration in_silico game noncorr
python3 -m spatial_egt.classification.feature_pairwise_games in_silico game all
python3 -m spatial_egt.classification.feature_pairwise_games in_silico game noncorr
python3 -m spatial_egt.classification.feature_entropy in_silico game all
python3 -m spatial_egt.classification.feature_entropy in_silico game noncorr
```