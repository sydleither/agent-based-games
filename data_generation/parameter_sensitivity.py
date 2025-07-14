from data_generation.main_data import main


experiment_name = "HAL"
num_samples = 2500
seed = 42
run_command = "sbatch job_abm.sb"

main(
    "data/in_silico2/raw",
    experiment_name,
    num_samples,
    seed,
    run_command,
    interaction_radius=4,
    reproduction_radius=2,
    end_time=300,
)

main(
    "data/in_silico3/raw",
    experiment_name,
    num_samples,
    seed,
    run_command,
    interaction_radius=6,
    reproduction_radius=3,
    end_time=300,
)
